package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"
)

// Raw export types needed for reading aep/out/*.json
type rawExportProject struct {
	File             string         `json:"file"`
	ExpressionEngine string         `json:"expressionEngine"`
	BitDepth         string         `json:"bitDepth"`
	Root             *rawExportItem `json:"root"`
}

type rawExportItem struct {
	ID         uint32           `json:"id"`
	Name       string           `json:"name"`
	Type       string           `json:"type"`
	Width      uint16           `json:"width,omitempty"`
	Height     uint16           `json:"height,omitempty"`
	Framerate  float64          `json:"framerate,omitempty"`
	Seconds    float64          `json:"seconds,omitempty"`
	Background string           `json:"backgroundColor,omitempty"`
	Footage    string           `json:"footageType,omitempty"`
	File       string           `json:"file,omitempty"`
	SolidColor []float64        `json:"solidColor,omitempty"`
	Layers     []rawExportLayer `json:"layers,omitempty"`
	Children   []*rawExportItem `json:"children,omitempty"`
}

type rawExportLayer struct {
	Index        uint32              `json:"index"`
	Name         string              `json:"name"`
	SourceID     uint32              `json:"sourceId"`
	ID           uint32              `json:"layerId"`
	Kind         string              `json:"kind"`
	ParentIndex  uint32              `json:"parentIndex,omitempty"`
	BlendMode    string              `json:"blendMode,omitempty"`
	StartTime    float64             `json:"startTime"`
	CompInPoint  float64             `json:"compInPoint"`
	CompOutPoint float64             `json:"compOutPoint"`
	Text         string              `json:"text,omitempty"`
	TextStyle    *rawTextStyle       `json:"textStyle,omitempty"`
	Flags        map[string]bool     `json:"flags"`
	Transform    []rawExportProperty `json:"transform,omitempty"`
	Effects      []rawExportProperty `json:"effects,omitempty"`
	Contents     []rawExportProperty `json:"contents,omitempty"`
}

type rawTextStyle struct {
	Font          string    `json:"font"`
	FontSize      float64   `json:"fontSize"`
	FillColor     []float64 `json:"fillColor"`
	Tracking      float64   `json:"tracking"`
	Justification string    `json:"justification"`
}

type rawExportProperty struct {
	Name       string              `json:"name"`
	MatchName  string              `json:"matchName"`
	Value      []float64           `json:"value,omitempty"`
	Animated   bool                `json:"animated,omitempty"`
	Expression string              `json:"expression,omitempty"`
	Keyframes  []rawExportKeyframe `json:"keyframes,omitempty"`
	Properties []rawExportProperty `json:"properties,omitempty"`
}

type rawExportKeyframe struct {
	CompTime float64   `json:"compTime"`
	Value    []float64 `json:"value,omitempty"`
}

// Target authoring model
type AuthoringProject struct {
	Schema           string                 `json:"$schema,omitempty"`
	File             string                 `json:"file,omitempty"`
	ExpressionEngine string                 `json:"expressionEngine,omitempty"`
	BitDepth         string                 `json:"bitDepth,omitempty"`
	Assets           []AuthoringAsset       `json:"assets,omitempty"`
	Compositions     []AuthoringComposition `json:"compositions"`
}

type AuthoringAsset struct {
	ID         string    `json:"id"`
	Name       string    `json:"name,omitempty"`
	Type       string    `json:"type"`
	File       string    `json:"file,omitempty"`
	Width      int       `json:"width,omitempty"`
	Height     int       `json:"height,omitempty"`
	SolidColor []float64 `json:"solidColor,omitempty"`
}

type AuthoringComposition struct {
	Name            string           `json:"name"`
	Width           int              `json:"width"`
	Height          int              `json:"height"`
	FPS             float64          `json:"fps"`
	Duration        float64          `json:"duration"`
	BackgroundColor string           `json:"backgroundColor,omitempty"`
	Layers          []AuthoringLayer `json:"layers"`
}

type AuthoringLayer struct {
	Name       string                 `json:"name"`
	Type       string                 `json:"type"`
	Parent     string                 `json:"parent,omitempty"`
	ThreeD     bool                   `json:"threeD,omitempty"`
	MotionBlur bool                   `json:"motionBlur,omitempty"`
	Collapse   bool                   `json:"collapse,omitempty"`
	In         *float64               `json:"in,omitempty"`
	Out        *float64               `json:"out,omitempty"`
	BlendMode  string                 `json:"blendMode,omitempty"`
	Transform  map[string]interface{} `json:"transform,omitempty"`
	Text       *AuthoringText         `json:"text,omitempty"`
}

type AuthoringText struct {
	String        string    `json:"string"`
	Font          string    `json:"font,omitempty"`
	FontSize      float64   `json:"fontSize,omitempty"`
	FillColor     []float64 `json:"fillColor,omitempty"`
	Tracking      float64   `json:"tracking,omitempty"`
	Justification string    `json:"justification,omitempty"`
}

func main() {
	inPath := flag.String("i", "", "input raw export json")
	outPath := flag.String("o", "", "output authoring json")
	flag.Parse()

	if *inPath == "" || *outPath == "" {
		fmt.Fprintln(os.Stderr, "Usage: export2author -i <raw_export.json> -o <authoring.json>")
		os.Exit(1)
	}

	data, err := os.ReadFile(*inPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading %s: %v\n", *inPath, err)
		os.Exit(1)
	}

	var raw rawExportProject
	if err := json.Unmarshal(data, &raw); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing JSON: %v\n", err)
		os.Exit(1)
	}

	auth := AuthoringProject{
		Schema:           "../schema/motion.schema.json",
		File:             raw.File,
		ExpressionEngine: raw.ExpressionEngine,
		BitDepth:         raw.BitDepth,
		Assets:           []AuthoringAsset{},
		Compositions:     []AuthoringComposition{},
	}

	// Walk tree to find compositions and assets
	walkItems(raw.Root, &auth)

	outData, err := json.MarshalIndent(auth, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error marshaling output: %v\n", err)
		os.Exit(1)
	}

	if err := os.WriteFile(*outPath, outData, 0644); err != nil {
		fmt.Fprintf(os.Stderr, "Error writing %s: %v\n", *outPath, err)
		os.Exit(1)
	}

	fmt.Printf("Successfully converted %s -> %s (%d comps, %d assets)\n",
		*inPath, *outPath, len(auth.Compositions), len(auth.Assets))
}

func walkItems(item *rawExportItem, auth *AuthoringProject) {
	if item == nil {
		return
	}
	switch item.Type {
	case "Composition":
		comp := AuthoringComposition{
			Name:            item.Name,
			Width:           int(item.Width),
			Height:          int(item.Height),
			FPS:             item.Framerate,
			Duration:        item.Seconds,
			BackgroundColor: item.Background,
			Layers:          []AuthoringLayer{},
		}

		// Layer index to name map for parenting
		nameByIndex := make(map[uint32]string)
		for _, l := range item.Layers {
			nameByIndex[l.Index] = l.Name
		}

		for _, l := range item.Layers {
			layerName := l.Name
			if layerName == "" {
				layerName = fmt.Sprintf("Layer %d", l.Index)
			}
			layerKind := l.Kind
			if layerKind == "av" {
				layerKind = "footage"
			}

			al := AuthoringLayer{
				Name:       layerName,
				Type:       layerKind,
				ThreeD:     l.Flags["3D"],
				MotionBlur: l.Flags["motionBlur"],
				Collapse:   l.Flags["collapse"],
				BlendMode:  l.BlendMode,
				Transform:  make(map[string]interface{}),
			}

			if l.CompInPoint > 0 {
				inVal := l.CompInPoint
				al.In = &inVal
			}
			if l.CompOutPoint > 0 && l.CompOutPoint > l.CompInPoint {
				outVal := l.CompOutPoint
				al.Out = &outVal
			}

			if l.ParentIndex > 0 {
				if parentName, ok := nameByIndex[l.ParentIndex]; ok {
					al.Parent = parentName
				}
			}

			if l.Text != "" || l.TextStyle != nil {
				al.Text = &AuthoringText{
					String: l.Text,
				}
				if l.TextStyle != nil {
					al.Text.Font = l.TextStyle.Font
					al.Text.FontSize = l.TextStyle.FontSize
					al.Text.FillColor = l.TextStyle.FillColor
					al.Text.Tracking = l.TextStyle.Tracking
					al.Text.Justification = l.TextStyle.Justification
				}
			}

			for _, prop := range l.Transform {
				propKey := mapTransformKey(prop.MatchName)
				if propKey == "" {
					continue
				}
				if prop.Animated {
					kfs := []map[string]interface{}{}
					for _, k := range prop.Keyframes {
						kfs = append(kfs, map[string]interface{}{
							"time":  k.CompTime,
							"value": k.Value,
						})
					}
					propObj := map[string]interface{}{
						"keyframes": kfs,
					}
					if prop.Expression != "" {
						propObj["expression"] = prop.Expression
					}
					al.Transform[propKey] = propObj
				} else if prop.Expression != "" {
					al.Transform[propKey] = map[string]interface{}{
						"value":      prop.Value,
						"expression": prop.Expression,
					}
				} else if len(prop.Value) > 0 {
					if len(prop.Value) == 1 {
						al.Transform[propKey] = prop.Value[0]
					} else {
						al.Transform[propKey] = prop.Value
					}
				}
			}

			comp.Layers = append(comp.Layers, al)
		}
		auth.Compositions = append(auth.Compositions, comp)

	case "Footage":
		asset := AuthoringAsset{
			ID:         fmt.Sprintf("asset_%d", item.ID),
			Name:       item.Name,
			Type:       item.Footage,
			File:       item.File,
			Width:      int(item.Width),
			Height:     int(item.Height),
			SolidColor: item.SolidColor,
		}
		if asset.Type == "" {
			asset.Type = "file"
		}
		auth.Assets = append(auth.Assets, asset)
	}

	for _, child := range item.Children {
		walkItems(child, auth)
	}
}

func mapTransformKey(matchName string) string {
	switch matchName {
	case "ADBE Position":
		return "position"
	case "ADBE Anchor Point":
		return "anchorPoint"
	case "ADBE Scale":
		return "scale"
	case "ADBE Rotate Z", "ADBE Rotation":
		return "rotation"
	case "ADBE Opacity":
		return "opacity"
	case "ADBE Position_0":
		return "xPosition"
	case "ADBE Position_1":
		return "yPosition"
	case "ADBE Rotate X":
		return "xRotation"
	case "ADBE Rotate Y":
		return "yRotation"
	case "ADBE Orientation":
		return "orientation"
	default:
		if strings.HasPrefix(matchName, "ADBE ") {
			return ""
		}
		return matchName
	}
}
