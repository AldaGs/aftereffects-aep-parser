package aep

import (
	"bytes"
	"encoding/binary"
	"math"

	"github.com/rioam2/rifx"
)

// KeyframeInterpolation enumerates the temporal interpolation type of a keyframe
type KeyframeInterpolation uint8

const (
	// KeyframeInterpolationLinear denotes linear interpolation
	KeyframeInterpolationLinear KeyframeInterpolation = 0x01
	// KeyframeInterpolationBezier denotes bezier (eased) interpolation
	KeyframeInterpolationBezier KeyframeInterpolation = 0x02
	// KeyframeInterpolationHold denotes hold (stepped) interpolation
	KeyframeInterpolationHold KeyframeInterpolation = 0x03
)

// String translates a keyframe interpolation enumeration to string
func (k KeyframeInterpolation) String() string {
	switch k {
	case KeyframeInterpolationLinear:
		return "Linear"
	case KeyframeInterpolationBezier:
		return "Bezier"
	case KeyframeInterpolationHold:
		return "Hold"
	default:
		return "Unknown"
	}
}

// PropertyValueType describes how the value of an animatable property is encoded
type PropertyValueType string

const (
	// PropertyValueTypeNone denotes a property whose value is not a plain number list
	// (eg: text documents, mask/shape paths, markers). Keyframe times are still parsed.
	PropertyValueTypeNone PropertyValueType = "NoValue"
	// PropertyValueTypeNumeric denotes a (multi-dimensional) numeric property
	PropertyValueTypeNumeric PropertyValueType = "Numeric"
	// PropertyValueTypeSpatial denotes a spatial (positional) property which has spatial tangents
	PropertyValueTypeSpatial PropertyValueType = "Spatial"
	// PropertyValueTypeColor denotes a color property. Values are [R, G, B, A] in the 0..1 range
	PropertyValueTypeColor PropertyValueType = "Color"
)

// Keyframe describes a single keyframe of an animated property
type Keyframe struct {
	// Time of the keyframe in seconds, relative to the start time of the layer (layer time)
	Time float64
	// CompTime is the time of the keyframe in seconds in the composition timeline
	// (layer start time + Time)
	CompTime float64
	// TimeRaw is the raw time stamp of the keyframe as stored in the project
	TimeRaw          int32
	InInterpolation  KeyframeInterpolation
	OutInterpolation KeyframeInterpolation
	// Value of the property at this keyframe (empty for NoValue properties)
	Value []float64
	// Temporal ease. Spatial properties have a single entry, other properties one per dimension.
	InSpeed      []float64
	InInfluence  []float64
	OutSpeed     []float64
	OutInfluence []float64
	// Spatial tangents (only for spatial properties)
	InTangent  []float64
	OutTangent []float64
}

// tdb4 field offsets (big endian)
const (
	tdb4OffsetDimensions = 2
	tdb4OffsetAttributes = 5
	tdb4OffsetNoValue    = 57
	tdb4OffsetColor      = 59
)

// parseAnimatableProperty fills value, keyframe and expression information of a property from
// its "tdbs" list. The tdbs list typically contains:
//
//	tdb4: property header (dimensions, flags)
//	cdat: static value (only used when the property is not animated)
//	list: keyframes (lhd3 header + ldat data)
//	Utf8: expression
func parseAnimatableProperty(prop *Property, tdbs *rifx.List) {
	tdb4Block, err := tdbs.FindByType("tdb4")
	if err != nil {
		return
	}
	header, ok := tdb4Block.Data.([]byte)
	if !ok || len(header) < tdb4OffsetColor+1 {
		return
	}

	dims := int(binary.BigEndian.Uint16(header[tdb4OffsetDimensions : tdb4OffsetDimensions+2]))
	attrs := header[tdb4OffsetAttributes]
	prop.Dimensions = dims
	switch {
	case header[tdb4OffsetNoValue]&0x01 != 0:
		prop.ValueType = PropertyValueTypeNone
	case header[tdb4OffsetColor] == 0x01:
		prop.ValueType = PropertyValueTypeColor
	case attrs&0x08 != 0:
		prop.ValueType = PropertyValueTypeSpatial
	default:
		prop.ValueType = PropertyValueTypeNumeric
	}

	// Static value
	if prop.ValueType != PropertyValueTypeNone {
		if cdatBlock, err := tdbs.FindByType("cdat"); err == nil {
			if data, ok := cdatBlock.Data.([]byte); ok {
				prop.Value = prop.normalizeValue(readFloats(data, 0, dims))
			}
		}
	}

	// Expression
	if exprBlock, err := tdbs.FindByType("Utf8"); err == nil {
		prop.Expression = exprBlock.ToString()
	}

	// Keyframes
	if listHead, err := tdbs.SublistFind("list"); err == nil {
		prop.Keyframes = parseKeyframes(prop, listHead)
		prop.Animated = len(prop.Keyframes) > 0
	}
}

func parseKeyframes(prop *Property, listHead *rifx.List) []*Keyframe {
	keyframes := make([]*Keyframe, 0)
	lhd3Block, err := listHead.FindByType("lhd3")
	if err != nil {
		return keyframes
	}
	lhd3, ok := lhd3Block.Data.([]byte)
	if !ok || len(lhd3) < 20 {
		return keyframes
	}
	count := int(binary.BigEndian.Uint16(lhd3[10:12]))
	itemSize := int(binary.BigEndian.Uint16(lhd3[18:20]))
	ldatBlock, err := listHead.FindByType("ldat")
	if err != nil || count == 0 || itemSize < 8 {
		return keyframes
	}
	ldat, ok := ldatBlock.Data.([]byte)
	if !ok {
		return keyframes
	}

	dims := prop.Dimensions
	for i := 0; i < count && (i+1)*itemSize <= len(ldat); i++ {
		item := ldat[i*itemSize : (i+1)*itemSize]
		kf := &Keyframe{
			TimeRaw:          int32(binary.BigEndian.Uint32(item[0:4])),
			InInterpolation:  KeyframeInterpolation(item[4]),
			OutInterpolation: KeyframeInterpolation(item[5]),
		}

		switch prop.ValueType {
		case PropertyValueTypeSpatial, PropertyValueTypeColor:
			// 8B header, 8B unknown, 8B distance to next keyframe, in speed, in influence,
			// out speed, out influence, value[dims], (spatial: in tangent[dims], out tangent[dims])
			if len(item) >= 56+dims*8 {
				kf.InSpeed = readFloats(item, 24, 1)
				kf.InInfluence = readFloats(item, 32, 1)
				kf.OutSpeed = readFloats(item, 40, 1)
				kf.OutInfluence = readFloats(item, 48, 1)
				kf.Value = prop.normalizeValue(readFloats(item, 56, dims))
			}
			if prop.ValueType == PropertyValueTypeSpatial && len(item) >= 56+dims*24 {
				kf.InTangent = readFloats(item, 56+dims*8, dims)
				kf.OutTangent = readFloats(item, 56+dims*16, dims)
			}
		case PropertyValueTypeNumeric:
			// 8B header, value[dims], in speed[dims], in influence[dims], out speed[dims], out influence[dims]
			if len(item) >= 8+dims*40 {
				kf.Value = prop.normalizeValue(readFloats(item, 8, dims))
				kf.InSpeed = prop.normalizeValue(readFloats(item, 8+dims*8, dims))
				kf.InInfluence = readFloats(item, 8+dims*16, dims)
				kf.OutSpeed = prop.normalizeValue(readFloats(item, 8+dims*24, dims))
				kf.OutInfluence = readFloats(item, 8+dims*32, dims)
			}
		}
		keyframes = append(keyframes, kf)
	}
	return keyframes
}

// parseOrientation handles the special "otst" list of the 3D orientation property, which
// stores its values (3 floats) outside of the regular tdbs data.
func parseOrientation(prop *Property, otst *rifx.List) {
	tdbs, err := otst.SublistFind("tdbs")
	if err != nil {
		return
	}
	parseAnimatableProperty(prop, tdbs)
	prop.ValueType = PropertyValueTypeSpatial
	prop.Dimensions = 3
	if cdatBlock, err := tdbs.FindByType("cdat"); err == nil {
		if data, ok := cdatBlock.Data.([]byte); ok {
			prop.Value = readFloats(data, 0, 3)
		}
	}
	if otky, err := otst.SublistFind("otky"); err == nil && len(prop.Keyframes) > 0 {
		idx := 0
		for _, block := range otky.Blocks {
			if block.Type != "otda" || idx >= len(prop.Keyframes) {
				continue
			}
			if data, ok := block.Data.([]byte); ok {
				prop.Keyframes[idx].Value = readFloats(data, 0, 3)
			}
			idx++
		}
	}
}

// normalizeValue converts colors from the stored ARGB 0..255 representation to RGBA 0..1,
// and scales layer Scale and Opacity from 0..1 to 0..100 percentages.
func (p *Property) normalizeValue(v []float64) []float64 {
	if p.ValueType == PropertyValueTypeColor && len(v) == 4 {
		return []float64{v[1] / 255, v[2] / 255, v[3] / 255, v[0] / 255}
	}
	if p.MatchName == "ADBE Scale" || p.MatchName == "ADBE Opacity" {
		scaled := make([]float64, len(v))
		for i, x := range v {
			scaled[i] = x * 100
		}
		return scaled
	}
	return v
}

func readFloats(data []byte, offset int, n int) []float64 {
	if n <= 0 || offset < 0 || offset+n*8 > len(data) {
		return nil
	}
	ret := make([]float64, n)
	reader := bytes.NewReader(data[offset : offset+n*8])
	for i := range ret {
		var bits uint64
		binary.Read(reader, binary.BigEndian, &bits)
		ret[i] = math.Float64frombits(bits)
	}
	return ret
}

// applyTimeBase converts raw keyframe times of a property tree to seconds
func applyTimeBase(props []*Property, timeBase float64, layerStart float64) {
	if timeBase == 0 {
		return
	}
	for _, p := range props {
		if p == nil {
			continue
		}
		for _, kf := range p.Keyframes {
			kf.Time = float64(kf.TimeRaw) / timeBase
			kf.CompTime = layerStart + kf.Time
		}
		applyTimeBase(p.Properties, timeBase, layerStart)
	}
}

