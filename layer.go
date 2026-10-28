package aep

import (
	"encoding/binary"

	"github.com/rioam2/rifx"
)

// LayerQualityLevel denotes the quality level of a layer (eg: Best, Draft, Wireframe)
type LayerQualityLevel uint16

const (
	// LayerQualityBest enumerates the value of a layer with Best Quality
	LayerQualityBest LayerQualityLevel = 0x0002
	// LayerQualityDraft enumerates the value of a layer with Draft Quality
	LayerQualityDraft LayerQualityLevel = 0x0001
	// LayerQualityWireframe enumerates the value of a layer with Wireframe Quality
	LayerQualityWireframe LayerQualityLevel = 0x0000
)

// LayerSamplingMode denotes the sampling mode of a layer (eg: Bilinear, Bicubic)
type LayerSamplingMode byte

const (
	// LayerSamplingModeBilinear enumerates the value of a layer with Bilinear Sampling
	LayerSamplingModeBilinear LayerSamplingMode = 0x00
	// LayerSamplingModeBicubic enumerates the value of a layer with Bicubic Sampling
	LayerSamplingModeBicubic LayerSamplingMode = 0x01
)

// LayerFrameBlendMode denotes the frame blending mode of a layer (eg: Frame mix, Pixel motion)
type LayerFrameBlendMode byte

const (
	// LayerFrameBlendModeFrameMix enumerates the value of a layer with Frame Mix Frame Blending
	LayerFrameBlendModeFrameMix LayerFrameBlendMode = 0x00
	// LayerFrameBlendModePixelMotion enumerates the value of a layer with Pixel Motion Frame Blending
	LayerFrameBlendModePixelMotion LayerFrameBlendMode = 0x01
)

// Layer describes a single layer in a composition.
type Layer struct {
	Index                    uint32
	ID                       uint32 // ldta layer id; what ParentID and MatteLayerID refer to
	ParentID                 uint32 // 0 = no parent
	MatteLayerID             uint32 // AE >= 23 only; 0 = none or older file
	BlendingMode             byte   // AE SDK PF_Xfer value, see blendModeNames
	TrackMatteType           byte   // 0 none, 1 alpha, 2 alpha inverted, 3 luma, 4 luma inverted
	LayerType                byte   // 0 AV, 1 light, 2 camera, 3 text, 4 shape
	NullLayer                bool
	Name                     string
	SourceID                 uint32
	StartTime                float64
	InPoint                  float64
	Duration                 float64
	Quality                  LayerQualityLevel
	SamplingMode             LayerSamplingMode
	FrameBlendMode           LayerFrameBlendMode
	GuideEnabled             bool
	SoloEnabled              bool
	ThreeDEnabled            bool
	AdjustmentLayerEnabled   bool
	CollapseTransformEnabled bool
	ShyEnabled               bool
	LockEnabled              bool
	FrameBlendEnabled        bool
	MotionBlurEnabled        bool
	EffectsEnabled           bool
	AudioEnabled             bool
	VideoEnabled             bool
	Transform                []*Property
	Effects                  []*Property
	Markers                  []float64
	Masks                    []*Property
	Contents                 []*Property
	Audio                    []*Property
	Properties               []*Property
	Text                     *Property
	TextContent              string
	TextStyle                *TextStyle
}

func parseLayer(layerHead *rifx.List, project *Project) (*Layer, error) {
	layer := &Layer{}

	type LDTA struct {
		Unknown00        [4]byte           // Offset 0B
		Quality          LayerQualityLevel // Offset 4B
		Unknown01        [6]byte           // Offset 6B
		StartDividend    int32             // Offset 12B
		StartDivisor     uint32            // Offset 16B
		InPointDividend  int32             // Offset 20B
		InPointDivisor   uint32            // Offset 24B
		DurationDividend int32             // Offset 28B
		DurationDivisor  uint32            // Offset 32B
		Unknown02        [1]byte           // Offset 36B
		LayerAttrBits    [3]byte           // Offset 37B
		SourceID         uint32            // Offset 40B
	}
	ldtaBlock, err := layerHead.FindByType("ldta")
	if err != nil {
		return nil, err
	}
	ldta := &LDTA{}
	ldtaBlock.ToStruct(ldta)
	layer.SourceID = ldta.SourceID
	// Offsets past the fixed prefix, from py-aep's LdtaChunk (MIT):
	// blending 99, track matte 107, layer type 131, parent 132, matte layer 160.
	if raw, ok := ldtaBlock.Data.([]byte); ok && len(raw) >= 136 {
		layer.ID = binary.BigEndian.Uint32(raw[0:4])
		layer.BlendingMode = raw[99]
		layer.TrackMatteType = raw[107]
		layer.LayerType = raw[131]
		layer.ParentID = binary.BigEndian.Uint32(raw[132:136])
		layer.NullLayer = raw[38]&(1<<7) != 0
		if len(raw) >= 164 {
			layer.MatteLayerID = binary.BigEndian.Uint32(raw[160:164])
		}
	}
	layer.Quality = ldta.Quality
	if ldta.StartDivisor != 0 {
		layer.StartTime = float64(ldta.StartDividend) / float64(ldta.StartDivisor)
	}
	if ldta.InPointDivisor != 0 {
		layer.InPoint = float64(ldta.InPointDividend) / float64(ldta.InPointDivisor)
	}
	if ldta.DurationDivisor != 0 {
		layer.Duration = float64(ldta.DurationDividend) / float64(ldta.DurationDivisor)
	}
	layer.SamplingMode = LayerSamplingMode((ldta.LayerAttrBits[0] & (1 << 6)) >> 6)
	layer.FrameBlendMode = LayerFrameBlendMode((ldta.LayerAttrBits[0] & (1 << 2)) >> 2)
	layer.GuideEnabled = ((ldta.LayerAttrBits[0] & (1 << 1)) >> 1) == 1
	layer.SoloEnabled = ((ldta.LayerAttrBits[1] & (1 << 3)) >> 3) == 1
	layer.ThreeDEnabled = ((ldta.LayerAttrBits[1] & (1 << 2)) >> 2) == 1
	layer.AdjustmentLayerEnabled = ((ldta.LayerAttrBits[1] & (1 << 1)) >> 1) == 1
	layer.CollapseTransformEnabled = ((ldta.LayerAttrBits[2] & (1 << 7)) >> 7) == 1
	layer.ShyEnabled = ((ldta.LayerAttrBits[2] & (1 << 6)) >> 6) == 1
	layer.LockEnabled = ((ldta.LayerAttrBits[2] & (1 << 5)) >> 5) == 1
	layer.FrameBlendEnabled = ((ldta.LayerAttrBits[2] & (1 << 4)) >> 4) == 1
	layer.MotionBlurEnabled = ((ldta.LayerAttrBits[2] & (1 << 3)) >> 3) == 1
	layer.EffectsEnabled = ((ldta.LayerAttrBits[2] & (1 << 2)) >> 2) == 1
	layer.AudioEnabled = ((ldta.LayerAttrBits[2] & (1 << 1)) >> 1) == 1
	layer.VideoEnabled = ((ldta.LayerAttrBits[2] & (1 << 0)) >> 0) == 1

	nameBlock, err := layerHead.FindByType("Utf8")
	if err != nil {
		return nil, err
	}
	layer.Name = nameBlock.ToString()

	mergedTDGP := layerHead.SublistMerge("tdgp")
	rootTDGP, _ := indexedGroupToMap(mergedTDGP)

	var pardCache map[string]*parTDef
	if project != nil {
		pardCache = project.pardCache
	}

	// Parse effects stack
	if effectsTDGP, ok := rootTDGP["ADBE Effect Parade"]; ok {
		effectsProp, err := parsePropertyWithPard(effectsTDGP, "ADBE Effect Parade", pardCache)
		if err != nil {
			return nil, err
		}
		layer.Effects = effectsProp.Properties
	} else {
		layer.Effects = make([]*Property, 0)
	}

	// Layer markers: only their times (layer time, seconds), which is what
	// marker-driven expressions read.
	if markerTDGP, ok := rootTDGP["ADBE Marker"]; ok {
		if markerProp, err := parsePropertyWithPard(markerTDGP, "ADBE Marker", pardCache); err == nil {
			for _, k := range markerProp.Keyframes {
				layer.Markers = append(layer.Markers, k.Time)
			}
		}
	}

	// Parse transform group
	if transformTDGP, ok := rootTDGP["ADBE Transform Group"]; ok {
		if transformProp, err := parsePropertyWithPard(transformTDGP, "ADBE Transform Group", pardCache); err == nil {
			layer.Transform = transformProp.Properties
		}
	}

	// Parse masks
	if masksTDGP, ok := rootTDGP["ADBE Mask Parade"]; ok {
		if masksProp, err := parsePropertyWithPard(masksTDGP, "ADBE Mask Parade", pardCache); err == nil {
			layer.Masks = masksProp.Properties
		}
	}

	// Parse shape layer contents
	if vectorsTDGP, ok := rootTDGP["ADBE Root Vectors Group"]; ok {
		if vectorsProp, err := parsePropertyWithPard(vectorsTDGP, "ADBE Root Vectors Group", pardCache); err == nil {
			layer.Contents = vectorsProp.Properties
		}
	}

	// Parse audio group
	if audioTDGP, ok := rootTDGP["ADBE Audio Group"]; ok {
		if audioProp, err := parsePropertyWithPard(audioTDGP, "ADBE Audio Group", pardCache); err == nil {
			layer.Audio = audioProp.Properties
		}
	}

	// Parse text layer properties
	if textTDGP, ok := rootTDGP["ADBE Text Properties"]; ok {
		textProp, err := parsePropertyWithPard(textTDGP, "ADBE Text Properties", pardCache)
		if err != nil {
			return nil, err
		}
		layer.Text = textProp
		if data := findTextDocumentData(textTDGP); data != nil {
			layer.TextContent = parseTextContent(data)
			layer.TextStyle = parseTextStyle(data)
		}
	}

	// Parse all root property groups in order
	if rootProp, err := parsePropertyWithPard(mergedTDGP, "Layer Properties", pardCache); err == nil {
		layer.Properties = rootProp.Properties
	}

	return layer, nil
}
