package aep

import (
	"bytes"
	"strings"
	"unicode/utf16"

	"github.com/rioam2/rifx"
)

// textRunMarker precedes the document's text string inside a "btdk" text document dictionary.
var textRunMarker = []byte("/1 [ << /0 << /0 (")

// findTextDocumentData recursively searches a list for a "btdk" sublist and returns
// the raw text document dictionary stored inside it.
func findTextDocumentData(l *rifx.List) []byte {
	for _, b := range l.Blocks {
		if sub, ok := b.Data.(*rifx.List); ok {
			if sub.Identifier == "btdk" {
				for _, inner := range sub.Blocks {
					if data, ok := inner.Data.([]byte); ok {
						return data
					}
				}
			}
			if data := findTextDocumentData(sub); data != nil {
				return data
			}
		}
	}
	return nil
}

// parseTextContent extracts the text string (UTF-16BE, BOM-prefixed, PostScript-escaped)
// from a text document dictionary. Returns an empty string if none is found.
func parseTextContent(data []byte) string {
	for offset := 0; offset < len(data); {
		idx := bytes.Index(data[offset:], textRunMarker)
		if idx < 0 {
			return ""
		}
		start := offset + idx + len(textRunMarker)
		offset = start

		var raw []byte
		for j := start; j < len(data); j++ {
			c := data[j]
			if c == '\\' && j+1 < len(data) {
				j++
				raw = append(raw, data[j])
				continue
			}
			if c == ')' {
				break
			}
			raw = append(raw, c)
		}
		if len(raw) < 2 || raw[0] != 0xfe || raw[1] != 0xff {
			continue
		}
		raw = raw[2:]
		u := make([]uint16, 0, len(raw)/2)
		for k := 0; k+1 < len(raw); k += 2 {
			u = append(u, uint16(raw[k])<<8|uint16(raw[k+1]))
		}
		text := string(utf16.Decode(u))
		// After Effects uses \r as the paragraph separator and terminates the text with one
		text = strings.ReplaceAll(text, "\r\n", "\n")
		text = strings.ReplaceAll(text, "\r", "\n")
		text = strings.ReplaceAll(text, "\u2029", "\n")
		return strings.TrimRight(text, "\n")
	}
	return ""
}

// TextStyle is the document-wide style of a text layer, read from the first
// character and paragraph style runs of its text document. Key numbers are
// from py-aep's TextDocument (MIT).
type TextStyle struct {
	Font          string    `json:"font,omitempty"`
	FontSize      float64   `json:"fontSize"`
	Tracking      float64   `json:"tracking,omitempty"`
	Leading       float64   `json:"leading,omitempty"` // 0 = auto
	FillColor     []float64 `json:"fillColor,omitempty"`
	StrokeColor   []float64 `json:"strokeColor,omitempty"`
	ApplyFill     bool      `json:"applyFill"`
	ApplyStroke   bool      `json:"applyStroke"`
	StrokeWidth   float64   `json:"strokeWidth"`
	Justification string    `json:"justification"`
	// Paragraph (box) text only: the box's top-left corner and size in
	// layer space. Point text has no box.
	BoxPos  []float64 `json:"boxPos,omitempty"`
	BoxSize []float64 `json:"boxSize,omitempty"`
}

var justificationNames = []string{"left", "right", "center", "justifyLeft", "justifyRight", "justifyCenter", "justifyFull"}


func parseTextStyle(data []byte) *TextStyle {
	cos := parseCOS(data)
	doc := cosAt(cos, "1", "1", 0)
	char, _ := cosAt(doc, "0", "6", "0", 0, "0", "0", "6").(map[string]interface{})
	para, _ := cosAt(doc, "0", "5", "0", 0, "0", "0", "5").(map[string]interface{})
	if char == nil {
		return nil
	}
	num := func(m map[string]interface{}, k string, or float64) float64 {
		if f, ok := m[k].(float64); ok {
			return f
		}
		return or
	}
	flag := func(k string, or bool) bool {
		if b, ok := char[k].(bool); ok {
			return b
		}
		return or
	}
	// A paint is {0: {1: [alpha, r, g, b]}}.
	color := func(k string) []float64 {
		argb, _ := cosAt(char[k], "0", "1").([]interface{})
		if len(argb) < 4 {
			return nil
		}
		out := make([]float64, 3)
		for i := range out {
			out[i], _ = argb[i+1].(float64)
		}
		return out
	}
	s := &TextStyle{
		FontSize:    num(char, "1", 0),
		Tracking:    num(char, "8", 0),
		FillColor:   color("53"),
		StrokeColor: color("54"),
		ApplyFill:   flag("56", true),
		ApplyStroke: flag("57", false),
		StrokeWidth: num(char, "63", 1),
	}
	if !flag("4", true) {
		s.Leading = num(char, "5", 0)
	}
	if idx, ok := char["0"].(float64); ok {
		if name, ok := cosAt(cos, "0", "1", "0", int(idx), "0", "0", "0").(string); ok {
			s.Font = name
		}
	}
	// The box outline is a run of vertices whose first and seventh are the
	// top-left and bottom-right corners (py-aep's box_text_size).
	if box, _ := cosAt(cos, "0", "8", "0", 0, "0", "1", "0").([]interface{}); len(box) >= 14 {
		f := func(i int) float64 { v, _ := box[i].(float64); return v }
		s.BoxPos = []float64{f(0), f(1)}
		s.BoxSize = []float64{f(12) - f(0), f(13) - f(1)}
	}
	if j := int(num(para, "0", 0)); j >= 0 && j < len(justificationNames) {
		s.Justification = justificationNames[j]
	}
	return s
}
