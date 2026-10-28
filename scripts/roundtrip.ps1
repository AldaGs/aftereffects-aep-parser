<#
.SYNOPSIS
    Full round-trip verification pipeline for After Effects AEP & Motion Schema JSON.

.DESCRIPTION
    Validates fidelity across:
    - Authoring JSON -> JSX -> Native AEP -> aep-parser -> JSON verification
    - Native AEP -> aep-parser -> export2author -> JSX -> Rebuilt AEP -> aep-parser -> Diff

.PARAMETER AuthoringJson
    Path to an authoring JSON file (e.g., schema/examples/title_card.json).

.PARAMETER AepPath
    Path to a native .aep file (e.g., aep/TOP5.aep).

.PARAMETER All
    Runs round-trip tests on all default schema examples.

.PARAMETER OutputDir
    Directory where intermediate test artifacts and parsed JSONs are stored.
#>

[CmdletBinding()]
param (
    [string]$AuthoringJson = "",
    [string]$AepPath = "",
    [switch]$All,
    [switch]$SkipBuild,
    [string]$OutputDir = "temp\roundtrip",
    [double]$Tolerance = 0.05
)

$ErrorActionPreference = "Stop"

# Ensure executables exist
$ParserExe = Join-Path $PSScriptRoot "..\aep-parser.exe"
$Json2JsxExe = Join-Path $PSScriptRoot "..\json2jsx.exe"
$Export2AuthorExe = Join-Path $PSScriptRoot "..\export2author.exe"

foreach ($exe in @($ParserExe, $Json2JsxExe, $Export2AuthorExe)) {
    if (-not (Test-Path $exe)) {
        Write-Error "Required executable not found: $exe. Please run 'go build ./cmd/...' first."
    }
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

function Assert-Close($val1, $val2, $msg, [ref]$failures) {
    $diff = [Math]::Abs([double]$val1 - [double]$val2)
    if ($diff -gt $Tolerance) {
        Write-Host "  [FAIL] ${msg}: Expected $val1, Got $val2 (diff: $diff > $Tolerance)" -ForegroundColor Red
        $failures.Value++
    } else {
        Write-Host "  [PASS] ${msg} ($val2)" -ForegroundColor Green
    }
}

function Assert-Equal($val1, $val2, $msg, [ref]$failures) {
    if ($val1 -ne $val2) {
        Write-Host "  [FAIL] ${msg}: Expected '$val1', Got '$val2'" -ForegroundColor Red
        $failures.Value++
    } else {
        Write-Host "  [PASS] ${msg} ($val2)" -ForegroundColor Green
    }
}

function Find-CompItem($item, $compName) {
    if ($null -eq $item) { return $null }
    if ($item.type -eq "Composition" -and $item.name -eq $compName) {
        return $item
    }
    if ($item.children) {
        foreach ($child in $item.children) {
            $found = Find-CompItem $child $compName
            if ($null -ne $found) { return $found }
        }
    }
    return $null
}

function Test-AuthoringRoundtrip([string]$jsonPath) {
    Write-Host "`n========================================================" -ForegroundColor Cyan
    Write-Host "ROUND-TRIP TEST: Authoring JSON -> AEP -> Parsed JSON" -ForegroundColor Cyan
    Write-Host "Input: $jsonPath" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Cyan

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($jsonPath)
    $jsxOut = Join-Path $OutputDir "$baseName.jsx"
    $aepOut = Join-Path $OutputDir "$baseName.aep"
    $parsedOut = Join-Path $OutputDir "$baseName`_parsed.json"

    $candidateAep = [System.IO.Path]::ChangeExtension($jsonPath, ".aep")
    if ($SkipBuild -and (Test-Path $candidateAep)) {
        $aepOut = $candidateAep
        Write-Host "Using existing AEP (-SkipBuild): $aepOut" -ForegroundColor Cyan
    } else {
        # Step 1: Compile JSON to JSX and build AEP via After Effects
        Write-Host "Step 1: Compiling authoring JSON to AEP via json2jsx..." -ForegroundColor Yellow
        $absAepOut = [System.IO.Path]::GetFullPath($aepOut)
        & $Json2JsxExe -i $jsonPath -o $jsxOut -aep $absAepOut -run -close
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path $aepOut)) {
            Write-Host "[FAIL] Failed to build $aepOut from $jsonPath" -ForegroundColor Red
            return $false
        }
        Write-Host "Successfully generated: $aepOut" -ForegroundColor Green
    }

    # Step 2: Parse generated AEP back to JSON
    Write-Host "Step 2: Parsing generated AEP back to raw JSON via aep-parser..." -ForegroundColor Yellow
    & $ParserExe -i $aepOut -o $parsedOut
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $parsedOut)) {
        Write-Host "[FAIL] Failed to parse $aepOut" -ForegroundColor Red
        return $false
    }
    Write-Host "Successfully parsed: $parsedOut" -ForegroundColor Green

    # Step 3: Validate parsed content against authoring spec
    Write-Host "Step 3: Verifying properties..." -ForegroundColor Yellow
    $authoringData = Get-Content $jsonPath -Raw | ConvertFrom-Json
    $parsedData = Get-Content $parsedOut -Raw | ConvertFrom-Json

    $failures = 0
    foreach ($expectedComp in $authoringData.compositions) {
        Write-Host "`nVerifying Composition '$($expectedComp.name)':" -ForegroundColor Magenta
        $actualComp = Find-CompItem $parsedData.root $expectedComp.name

        if ($null -eq $actualComp) {
            Write-Host "  [FAIL] Composition '$($expectedComp.name)' not found in parsed AEP!" -ForegroundColor Red
            $failures++
            continue
        }

        Assert-Equal $expectedComp.width $actualComp.width "Comp Width" ([ref]$failures)
        Assert-Equal $expectedComp.height $actualComp.height "Comp Height" ([ref]$failures)
        if ($expectedComp.fps) {
            Assert-Close $expectedComp.fps $actualComp.framerate "Comp FPS" ([ref]$failures)
        }
        Assert-Close $expectedComp.duration $actualComp.seconds "Comp Duration (s)" ([ref]$failures)

        # Layer verification
        if ($expectedComp.layers) {
            $expectedLayerCount = $expectedComp.layers.Count
            $actualLayerCount = if ($actualComp.layers) { $actualComp.layers.Count } else { 0 }
            Assert-Equal $expectedLayerCount $actualLayerCount "Comp Layer Count" ([ref]$failures)

            for ($i = 0; $i -lt $expectedLayerCount; $i++) {
                $el = $expectedComp.layers[$i]
                $al = if ($actualComp.layers -and $i -lt $actualComp.layers.Count) { $actualComp.layers[$i] } else { $null }

                if ($null -eq $al) {
                    Write-Host "  [FAIL] Layer index $i ($($el.name)) missing in parsed AEP" -ForegroundColor Red
                    $failures++
                    continue
                }

                Write-Host "  Checking Layer [$i] '$($el.name)':" -ForegroundColor DarkGray
                Assert-Equal $el.name $al.name "Layer Name" ([ref]$failures)

                if ($el.parent) {
                    # Look up parent layer index
                    $parentLayer = $actualComp.layers | Where-Object { $_.name -eq $el.parent } | Select-Object -First 1
                    if ($parentLayer) {
                        Assert-Equal $parentLayer.index $al.parentIndex "Parent Layer Index" ([ref]$failures)
                    }
                }

                if ($el.text -and $al.text) {
                    Assert-Equal $el.text.string $al.text "Text String" ([ref]$failures)
                }

                if ($el.transform) {
                    # Check position keyframes or values
                    $posProp = $al.transform | Where-Object { $_.matchName -eq "ADBE Position" } | Select-Object -First 1
                    if ($posProp -and $el.transform.position) {
                        $authPos = $el.transform.position
                        if ($authPos.keyframes) {
                            Assert-Equal $authPos.keyframes.Count $posProp.keyframes.Count "Position Keyframe Count" ([ref]$failures)
                            for ($k = 0; $k -lt [Math]::Min($authPos.keyframes.Count, $posProp.keyframes.Count); $k++) {
                                Assert-Close $authPos.keyframes[$k].time $posProp.keyframes[$k].compTime "Keyframe $k Time" ([ref]$failures)
                            }
                        }
                    }

                    # Check opacity keyframes or values
                    $opProp = $al.transform | Where-Object { $_.matchName -eq "ADBE Opacity" } | Select-Object -First 1
                    if ($opProp -and $el.transform.opacity) {
                        $authOp = $el.transform.opacity
                        if ($authOp.keyframes) {
                            Assert-Equal $authOp.keyframes.Count $opProp.keyframes.Count "Opacity Keyframe Count" ([ref]$failures)
                        }
                    }
                }
            }
        }
    }

    if ($failures -eq 0) {
        Write-Host "`n>>> [SUCCESS] Round-trip verification passed for $jsonPath!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "`n>>> [FAILURE] $failures check(s) failed for $jsonPath" -ForegroundColor Red
        return $false
    }
}

function Test-NativeAepRoundtrip([string]$nativeAepPath) {
    Write-Host "`n========================================================" -ForegroundColor Cyan
    Write-Host "ROUND-TRIP TEST: Native AEP -> Authoring -> JSX -> Rebuilt AEP" -ForegroundColor Cyan
    Write-Host "Input: $nativeAepPath" -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Cyan

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($nativeAepPath)
    $origExportJson = Join-Path $OutputDir "$baseName`_orig.json"
    $authoringJson = Join-Path $OutputDir "$baseName`_authoring.json"
    $rebuiltJsx = Join-Path $OutputDir "$baseName`_rebuilt.jsx"
    $rebuiltAep = Join-Path $OutputDir "$baseName`_rebuilt.aep"
    $rebuiltExportJson = Join-Path $OutputDir "$baseName`_rebuilt_export.json"

    # Step 1: Parse original AEP
    Write-Host "Step 1: Parsing original AEP..." -ForegroundColor Yellow
    & $ParserExe -i $nativeAepPath -o $origExportJson
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to parse $nativeAepPath" -ForegroundColor Red
        return $false
    }

    # Step 2: Convert to authoring format
    Write-Host "Step 2: Converting to authoring JSON..." -ForegroundColor Yellow
    & $Export2AuthorExe -i $origExportJson -o $authoringJson
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to convert to authoring JSON" -ForegroundColor Red
        return $false
    }

    # Step 3: Compile to JSX and Rebuilt AEP
    Write-Host "Step 3: Compiling to JSX and building reconstructed AEP..." -ForegroundColor Yellow
    $absRebuiltAep = [System.IO.Path]::GetFullPath($rebuiltAep)
    & $Json2JsxExe -i $authoringJson -o $rebuiltJsx -aep $absRebuiltAep -run -close
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $rebuiltAep)) {
        Write-Host "[FAIL] Failed to rebuild AEP via After Effects" -ForegroundColor Red
        return $false
    }

    # Step 4: Parse reconstructed AEP
    Write-Host "Step 4: Parsing reconstructed AEP..." -ForegroundColor Yellow
    & $ParserExe -i $rebuiltAep -o $rebuiltExportJson
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] Failed to parse rebuilt AEP" -ForegroundColor Red
        return $false
    }

    # Step 5: Diff Compositions and Layers
    Write-Host "Step 5: Comparing original and reconstructed projects..." -ForegroundColor Yellow
    $orig = Get-Content $origExportJson -Raw | ConvertFrom-Json
    $rebuilt = Get-Content $rebuiltExportJson -Raw | ConvertFrom-Json

    $failures = 0
    # Find all comps in original
    $origComps = @()
    function Collect-Comps($item) {
        if ($null -eq $item) { return }
        if ($item.type -eq "Composition") { $script:origComps += $item }
        if ($item.children) { foreach ($c in $item.children) { Collect-Comps $c } }
    }
    Collect-Comps $orig.root

    foreach ($comp in $origComps) {
        Write-Host "`nComparing Comp '$($comp.name)':" -ForegroundColor Magenta
        $rebComp = Find-CompItem $rebuilt.root $comp.name
        if ($null -eq $rebComp) {
            Write-Host "  [FAIL] Missing comp '$($comp.name)' in rebuilt AEP" -ForegroundColor Red
            $failures++
            continue
        }

        Assert-Equal $comp.width $rebComp.width "Width" ([ref]$failures)
        Assert-Equal $comp.height $rebComp.height "Height" ([ref]$failures)
        Assert-Close $comp.framerate $rebComp.framerate "Framerate" ([ref]$failures)
        Assert-Close $comp.seconds $rebComp.seconds "Duration" ([ref]$failures)

        $origLayerCount = if ($comp.layers) { $comp.layers.Count } else { 0 }
        $rebLayerCount = if ($rebComp.layers) { $rebComp.layers.Count } else { 0 }
        Assert-Equal $origLayerCount $rebLayerCount "Layer Count" ([ref]$failures)
    }

    if ($failures -eq 0) {
        Write-Host "`n>>> [SUCCESS] Native AEP round-trip passed for $nativeAepPath!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "`n>>> [FAILURE] $failures diff(s) found for $nativeAepPath" -ForegroundColor Red
        return $false
    }
}

# Execution Dispatcher
$totalTests = 0
$passedTests = 0

if ($All) {
    $exampleFiles = @(
        "schema\examples\title_card.json",
        "schema\examples\lower_third.json",
        "schema\examples\shape_loop.json"
    )
    foreach ($file in $exampleFiles) {
        $totalTests++
        $fullPath = Join-Path $PSScriptRoot "..\" | Join-Path -ChildPath $file
        if (Test-AuthoringRoundtrip $fullPath) {
            $passedTests++
        }
    }
} elseif ($AuthoringJson) {
    $totalTests++
    if (Test-AuthoringRoundtrip $AuthoringJson) {
        $passedTests++
    }
} elseif ($AepPath) {
    $totalTests++
    if (Test-NativeAepRoundtrip $AepPath) {
        $passedTests++
    }
} else {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  powershell scripts\roundtrip.ps1 -All"
    Write-Host "  powershell scripts\roundtrip.ps1 -AuthoringJson schema\examples\title_card.json"
    Write-Host "  powershell scripts\roundtrip.ps1 -AepPath aep\TOP5.aep"
    exit 0
}

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY: $passedTests / $totalTests PASSED" -ForegroundColor $(if ($passedTests -eq $totalTests) { "Green" } else { "Red" })
Write-Host "========================================================`n" -ForegroundColor Cyan

if ($passedTests -ne $totalTests) {
    exit 1
}
