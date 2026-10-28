package aep

import (
	"bytes"
	"encoding/binary"
)

// SourceLayer is the layer of a layered PSD or Illustrator/PDF file that a
// footage item references (After Effects' "import as composition" makes one
// item per layer). Layouts from py-aep's PsdOptiChunk / TextOptiChunk (MIT).
type SourceLayer struct {
	// Index is the 0-based layer index: the PSD layer record (counting group
	// dividers) or the PDF optional-content group order. -1 when unknown.
	Index int    `json:"index"`
	Name  string `json:"name,omitempty"`
	ID    uint32 `json:"id,omitempty"` // Photoshop layer id (lyid)
	// Bounds is the layer's box (left, top, right, bottom) in document
	// pixels (PSD) or page points (AI/PDF).
	Bounds [4]float64 `json:"bounds"`
	// Canvas is the document size in the same units.
	Canvas [2]float64 `json:"canvas"`
	// FullFrame is true for a Document Size import (the footage is the whole
	// canvas, layer in place) and false for Layer Size (cropped to Bounds).
	FullFrame bool `json:"fullFrame"`
}

func cString(b []byte) string {
	if i := bytes.IndexByte(b, 0); i >= 0 {
		b = b[:i]
	}
	return string(b)
}

func parseSourceLayer(opti, sspc []byte) *SourceLayer {
	full := len(sspc) > 0xC7 && sspc[0xC7] != 0
	switch {
	case len(opti) >= 344 && string(opti[:4]) == "8BPS":
		idx := binary.BigEndian.Uint32(opti[14:18])
		if idx == 0xFFFFFFFF {
			return nil
		}
		le := func(o int) float64 { return float64(int32(binary.LittleEndian.Uint32(opti[o : o+4]))) }
		l := &SourceLayer{
			Index:     int(idx),
			ID:        binary.LittleEndian.Uint32(opti[340:344]),
			Bounds:    [4]float64{le(82), le(78), le(90), le(86)},
			Canvas:    [2]float64{le(36), le(32)},
			FullFrame: full,
		}
		if len(opti) > 344 {
			l.Name = cString(opti[344:])
		}
		return l
	case len(opti) >= 0x48 && string(opti[:4]) == "TEXT":
		name := cString(opti[0x44:])
		if name == "" {
			return nil
		}
		fx := func(o int) float64 { return float64(int32(binary.BigEndian.Uint32(opti[o:o+4]))) / 65536 }
		return &SourceLayer{
			Index:     -1,
			Name:      name,
			Bounds:    [4]float64{fx(0x10), fx(0x14), fx(0x18), fx(0x1C)},
			Canvas:    pageSize(opti),
			FullFrame: full,
		}
	}
	return nil
}

// pageSize is an AI/PDF opti's page (BE u16 height, width at 0x248), or the
// integral artwork box corner when the tail is missing.
func pageSize(opti []byte) [2]float64 {
	if len(opti) >= 0x24C+2 {
		return [2]float64{float64(binary.BigEndian.Uint16(opti[0x24C:])), float64(binary.BigEndian.Uint16(opti[0x248:]))}
	}
	return [2]float64{float64(binary.BigEndian.Uint16(opti[0x18:])), float64(binary.BigEndian.Uint16(opti[0x1C:]))}
}
