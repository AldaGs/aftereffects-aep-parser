package aep

import (
	"math"
	"bytes"
	"encoding/binary"
	"fmt"
	"strings"

	"github.com/rioam2/rifx"
)

// PropertyTypeName enumerates the value/type of a property
type PropertyTypeName uint16

const (
	// PropertyTypeBoolean denotes a boolean checkbox property
	PropertyTypeBoolean PropertyTypeName = 0x04
	// PropertyTypeOneD denotes a one-dimensional slider property
	PropertyTypeOneD PropertyTypeName = 0x02
	// PropertyTypeTwoD denotes a two-dimensional point property
	PropertyTypeTwoD PropertyTypeName = 0x06
	// PropertyTypeThreeD denotes a three-dimensional point property
	PropertyTypeThreeD PropertyTypeName = 0x12
	// PropertyTypeColor denotes a four-dimensional color property
	PropertyTypeColor PropertyTypeName = 0x05
	// PropertyTypeAngle denotes a one-dimensional angle property
	PropertyTypeAngle PropertyTypeName = 0x03
	// PropertyTypeLayerSelect denotes a single-valued layer selection property
	PropertyTypeLayerSelect PropertyTypeName = 0x00
	// PropertyTypeSelect denotes a single-valued selection property
	PropertyTypeSelect PropertyTypeName = 0x07
	// PropertyTypeGroup denotes a collection/group property
	PropertyTypeGroup PropertyTypeName = 0x0d
	// PropertyTypeCustom denotes an unknown/custom property type (default)
	PropertyTypeCustom PropertyTypeName = 0x0f
)

// String translates a property type enumeration to string
func (p PropertyTypeName) String() string {
	switch p {
	case PropertyTypeBoolean:
		return "Boolean"
	case PropertyTypeOneD:
		return "OneD"
	case PropertyTypeTwoD:
		return "TwoD"
	case PropertyTypeThreeD:
		return "ThreeD"
	case PropertyTypeColor:
		return "Color"
	case PropertyTypeAngle:
		return "Angle"
	case PropertyTypeLayerSelect:
		return "LayerSelect"
	case PropertyTypeSelect:
		return "Select"
	case PropertyTypeGroup:
		return "Group"
	default:
		return "Custom"
	}
}

// Property describes a property object of a layer or nested property
type Property struct {
	MatchName     string
	Name          string
	Label         string
	Index         uint32
	PropertyType  PropertyTypeName
	Properties    []*Property
	SelectOptions []string
	// Animation data (only populated for animatable leaf properties)
	ValueType  PropertyValueType
	Dimensions int
	Value      []float64
	Animated   bool
	Keyframes  []*Keyframe
	Expression string
	// Paths holds a bezier path property's values: one per keyframe, or one
	// for a static path. Mask paths are normalized to the layer size.
	Paths []*PathShape
	// Mask atoms only, from their `mkif` chunk.
	MaskInverted bool
	MaskMode     string
	// Arbitrary-data effect parameters only: the raw `aRbp` bytes.
	Arb []byte
}

var maskModeNames = []string{"none", "add", "subtract", "intersect", "lighten", "darken", "difference"}

// parseMaskInfo reads a mask's `mkif` chunk (py-aep, MIT): byte 0 is the
// invert flag, bytes 6-7 the SDK PF_MaskMode.
func parseMaskInfo(prop *Property, entries []interface{}) {
	for _, e := range entries {
		b, ok := e.(*rifx.Block)
		if !ok || b.Type != "mkif" {
			continue
		}
		if d, ok := b.Data.([]byte); ok && len(d) >= 8 {
			prop.MaskInverted = d[0] == 1
			if m := int(binary.BigEndian.Uint16(d[6:8])); m < len(maskModeNames) {
				prop.MaskMode = maskModeNames[m]
			}
		}
	}
}

var defaultPropertyNames = map[string]string{
	"ADBE Effect Parade":          "Effects",
	"ADBE Transform Group":        "Transform",
	"ADBE Anchor Point":           "Anchor Point",
	"ADBE Position":               "Position",
	"ADBE Position_0":             "X Position",
	"ADBE Position_1":             "Y Position",
	"ADBE Position_2":             "Z Position",
	"ADBE Scale":                  "Scale",
	"ADBE Orientation":            "Orientation",
	"ADBE Rotate X":               "X Rotation",
	"ADBE Rotate Y":               "Y Rotation",
	"ADBE Rotate Z":               "Rotation",
	"ADBE Opacity":                "Opacity",
	"ADBE Audio Group":            "Audio",
	"ADBE Audio Levels":           "Audio Levels",
	"ADBE Time Remapping":         "Time Remap",
	"ADBE Marker":                 "Marker",
	"ADBE Mask Parade":            "Masks",
	"ADBE Mask Atom":              "Mask",
	"ADBE Mask Shape":             "Mask Path",
	"ADBE Mask Feather":           "Mask Feather",
	"ADBE Mask Opacity":           "Mask Opacity",
	"ADBE Mask Offset":            "Mask Expansion",
	"ADBE Root Vectors Group":     "Contents",
	"ADBE Vector Group":           "Shape Group",
	"ADBE Vectors Group":          "Contents",
	"ADBE Vector Transform Group": "Transform",
	"ADBE Vector Anchor":          "Anchor Point",
	"ADBE Vector Position":        "Position",
	"ADBE Vector Scale":           "Scale",
	"ADBE Vector Skew":            "Skew",
	"ADBE Vector Skew Axis":       "Skew Axis",
	"ADBE Vector Rotation":        "Rotation",
	"ADBE Vector Group Opacity":   "Opacity",
	"ADBE Text Properties":        "Text",
	"ADBE Text Document":          "Source Text",
	"ADBE Text Path Options":      "Path Options",
	"ADBE Text More Options":      "More Options",
	"ADBE Text Animators":         "Animators",
	"ADBE Text Animator":          "Animator",
	"ADBE Text Selectors":         "Selectors",
	"ADBE Text Selector":          "Range Selector",
	"ADBE Text Animator Properties": "Animator Properties",
	"ADBE Layer Styles":           "Layer Styles",
	"ADBE Material Options Group": "Material Options",
	"ADBE Extrsn Options Group":   "Geometry Options",
	"ADBE Camera Options Group":   "Camera Options",
	"ADBE Light Options Group":    "Light Options",
}

func parseProperty(propData interface{}, matchName string) (*Property, error) {
	return parsePropertyWithPard(propData, matchName, nil)
}

func parsePropertyWithPard(propData interface{}, matchName string, pardCache map[string]*parTDef) (*Property, error) {
	prop := &Property{}

	// Apply some sensible default values
	prop.PropertyType = PropertyTypeCustom
	prop.SelectOptions = make([]string, 0)
	prop.MatchName = matchName
	prop.Name = matchName
	if friendly, ok := defaultPropertyNames[matchName]; ok {
		prop.Name = friendly
	}

	// Handle different types of property data
	switch propData.(type) {
	case *rifx.List:
		propHead := propData.(*rifx.List)
		if propHead == nil {
			return prop, nil
		}
		// Parse sub-properties
		prop.Properties = make([]*Property, 0)

		if tdsnBlock, err := propHead.FindByType("tdsn"); err == nil {
			label := tdsnBlock.ToString()
			if label != "" && label != "-_0_/-" {
				prop.Label = label
			}
		}

		switch propHead.Identifier {
		case "tdbs":
			parseAnimatableProperty(prop, propHead)
			return prop, nil
		case "otst":
			parseOrientation(prop, propHead)
			return prop, nil
		case "btds", "mrst", "om-s":
			if tdbs, err := propHead.SublistFind("tdbs"); err == nil {
				parseAnimatableProperty(prop, tdbs)
			}
			if propHead.Identifier == "om-s" {
				prop.Paths = parseShapes(propHead)
			}
			return prop, nil
		}

		subProps, orderedMatchNames := indexedGroupToEntries(propHead)
		_, contents := pairMatchNames(propHead)
		for idx, mn := range orderedMatchNames {
			subProp, err := parsePropertyWithPard(subProps[idx], mn, pardCache)
			if err == nil {
				subProp.Index = uint32(idx) + 1
				if mn == "ADBE Mask Atom" && idx < len(contents) {
					parseMaskInfo(subProp, contents[idx])
				}
				prop.Properties = append(prop.Properties, subProp)
			}
		}

		// Parse effect sub-properties
		if propHead.Identifier == "sspc" {
			prop.PropertyType = PropertyTypeGroup
			fnamBlock, err := propHead.FindByType("fnam")
			if err == nil {
				prop.Name = fnamBlock.ToString()
			}
			tdgpBlock, err := propHead.SublistFind("tdgp")
			var effectTDGP []*rifx.List
			var effectTDGPMNs []string
			arbByMN := map[string][]byte{}
			if err == nil {
				// Look for a tdsn which specifies the user-defined label of the property
				tdsnBlock, err := tdgpBlock.FindByType("tdsn")
				if err == nil {
					label := fmt.Sprintf("%s", tdsnBlock.ToString())

					// Check if there is a custom user defined label added. The default if there
					// is not is "-_0_/-" for some unknown reason.
					if label != "-_0_/-" {
						prop.Label = label
					}
				}
				effectTDGP, effectTDGPMNs = indexedGroupToEntries(tdgpBlock)
				// An arbitrary-data parameter keeps its bytes in an `aRbp`
				// chunk, in a list beside the usual `tdbs`.
				mns, contents := pairMatchNames(tdgpBlock)
				for i, mn := range mns {
					for _, c := range contents[i] {
						if l, ok := c.(*rifx.List); ok {
							if b, err := l.FindByType("aRbp"); err == nil {
								if data, ok := b.Data.([]byte); ok {
									arbByMN[mn] = data
								}
							}
						}
					}
				}
			}
			parTList := propHead.SublistMerge("parT")
			subPropMatchNames, subPropPards := pairMatchNames(parTList)
			if len(subPropMatchNames) > 0 && pardCache != nil {
				pardCache[matchName] = &parTDef{matchNames: subPropMatchNames, pards: subPropPards}
			} else if len(subPropMatchNames) == 0 && pardCache != nil {
				if cached, ok := pardCache[matchName]; ok {
					subPropMatchNames = cached.matchNames
					subPropPards = cached.pards
				}
			}

			tdgpByMN := make(map[string]*rifx.List, len(effectTDGPMNs))
			for idx, mn := range effectTDGPMNs {
				if idx < len(effectTDGP) {
					tdgpByMN[mn] = effectTDGP[idx]
				}
			}

			if len(subPropMatchNames) > 0 {
				for idx, mn := range subPropMatchNames {
					// Skip first pard entry (describes parent)
					if idx == 0 {
						continue
					}
					subProp, err := parsePropertyWithPard(subPropPards[idx], mn, pardCache)
					if err == nil {
						subProp.Index = uint32(idx)
						if tdgpEntry, ok := tdgpByMN[mn]; ok && tdgpEntry != nil {
							attachEffectTDGP(subProp, tdgpEntry)
						}
						subProp.Arb = arbByMN[mn]
						prop.Properties = append(prop.Properties, subProp)
					}
				}
			} else if len(effectTDGPMNs) > 1 {
				for idx := 1; idx < len(effectTDGPMNs); idx++ {
					subProp, err := parsePropertyWithPard(effectTDGP[idx], effectTDGPMNs[idx], pardCache)
					if err == nil {
						subProp.Index = uint32(idx)
						if subProp.Label != "" {
							subProp.Name = subProp.Label
							subProp.Label = ""
						}
						prop.Properties = append(prop.Properties, subProp)
					}
				}
			}
		}
	case []interface{}:
		for _, entry := range propData.([]interface{}) {
			if block, ok := entry.(*rifx.Block); ok {
				switch block.Type {
				case "pdnm":
					strContent := block.ToString()
					if prop.PropertyType == PropertyTypeSelect {
						prop.SelectOptions = strings.Split(strContent, "|")
					} else if strContent != "" {
						prop.Name = strContent
					}
				case "pard":
					blockData := block.Data.([]byte)
					prop.PropertyType = PropertyTypeName(binary.BigEndian.Uint16(blockData[14:16]))
					if prop.PropertyType == 0x0a {
						prop.PropertyType = PropertyTypeOneD
					}
					// The control's current value, for parameters whose
					// value the effect never stored (left at the default).
					// Layouts from py-aep (MIT).
					if len(blockData) >= 64 {
						switch blockData[15] {
						case 10: // float slider: f8
							prop.Value = []float64{math.Float64frombits(binary.BigEndian.Uint64(blockData[56:64]))}
						case 4: // checkbox: u4
							prop.Value = []float64{float64(binary.BigEndian.Uint32(blockData[56:60]))}
						case 1: // integer slider: s4
							prop.Value = []float64{float64(int32(binary.BigEndian.Uint32(blockData[56:60])))}
						}
					}
					pardName := fmt.Sprintf("%s", bytes.Trim(blockData[16:48], "\x00"))
					if pardName != "" {
						prop.Name = pardName
					}
				}
			}
		}
	}

	return prop, nil
}

type parTDef struct {
	matchNames []string
	pards      [][]interface{}
}

func attachEffectTDGP(prop *Property, tdgpEntry *rifx.List) {
	fromPard := prop.Value
	defer func() {
		if len(prop.Value) == 0 && len(prop.Keyframes) == 0 {
			prop.Value = fromPard
		}
	}()
	if tdgpEntry.Identifier == "tdbs" {
		parseAnimatableProperty(prop, tdgpEntry)
	} else if tdbs, err := tdgpEntry.SublistFind("tdbs"); err == nil {
		parseAnimatableProperty(prop, tdbs)
	}
}

func pairMatchNames(head *rifx.List) ([]string, [][]interface{}) {
	matchNames := make([]string, 0)
	datum := make([][]interface{}, 0)
	if head != nil {
		groupIdx := -1
		skipToNextTDMNFlag := false
		for _, block := range head.Blocks {
			if block.Type == "tdmn" {
				matchName := fmt.Sprintf("%s", bytes.Trim(block.Data.([]byte), "\x00"))
				if matchName == "ADBE Group End" || matchName == "ADBE Effect Built In Params" {
					skipToNextTDMNFlag = true
					continue
				}
				matchNames = append(matchNames, matchName)
				skipToNextTDMNFlag = false
				groupIdx++
			} else if groupIdx >= 0 && !skipToNextTDMNFlag {
				if groupIdx >= len(datum) {
					datum = append(datum, make([]interface{}, 0))
				}
				switch block.Data.(type) {
				case *rifx.List:
					datum[groupIdx] = append(datum[groupIdx], block.Data)
				default:
					datum[groupIdx] = append(datum[groupIdx], block)
				}
			}
		}
	}
	return matchNames, datum
}

func indexedGroupToMap(tdgpHead *rifx.List) (map[string]*rifx.List, []string) {
	tdgpMap := make(map[string]*rifx.List, 0)
	lists, matchNames := indexedGroupToEntries(tdgpHead)
	for idx, matchName := range matchNames {
		if lists[idx] != nil {
			tdgpMap[matchName] = lists[idx]
		}
	}
	return tdgpMap, matchNames
}

func indexedGroupToEntries(tdgpHead *rifx.List) ([]*rifx.List, []string) {
	matchNames, contents := pairMatchNames(tdgpHead)
	lists := make([]*rifx.List, len(matchNames))
	for idx := range matchNames {
		// The property list is usually the first entry, but a mask atom puts
		// its `mkif` info chunk first: take the first list.
		if idx < len(contents) {
			for _, c := range contents[idx] {
				if l, ok := c.(*rifx.List); ok {
					lists[idx] = l
					break
				}
			}
		}
	}
	return lists, matchNames
}
