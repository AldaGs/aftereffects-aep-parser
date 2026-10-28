package aep

import (
	"encoding/binary"
	"math"

	"github.com/rioam2/rifx"
)

// PathShape is one value of a bezier path property: AE's Shape, with
// tangents relative to their vertex as ExtendScript reports them.
type PathShape struct {
	Closed      bool
	Vertices    [][2]float64
	InTangents  [][2]float64
	OutTangents [][2]float64
}

// parseShapes reads every value of an om-s path property, one per keyframe
// (or a single one when static). Layout from py-aep's `parse_shape` (MIT):
// om-s > omks > shap > { shph, LIST list > ldat }. A `shph` holds the open
// flag and a bounding box; `ldat` holds float32 points normalized to that box,
// in triples of (vertex, out handle, in handle of the next vertex), handles
// absolute.
func parseShapes(oms *rifx.List) []*PathShape {
	omks, err := oms.SublistFind("omks")
	if err != nil {
		return nil
	}
	var out []*PathShape
	for _, shap := range omks.SublistFilter("shap") {
		shph, err := shap.FindByType("shph")
		if err != nil {
			continue
		}
		h, ok := shph.Data.([]byte)
		if !ok || len(h) < 20 {
			continue
		}
		f := func(b []byte) float64 { return float64(math.Float32frombits(binary.BigEndian.Uint32(b))) }
		x0, y0, x1, y1 := f(h[4:]), f(h[8:]), f(h[12:]), f(h[16:])
		s := &PathShape{Closed: h[3]&(1<<3) == 0}
		var raw []byte
		if list, err := shap.SublistFind("list"); err == nil {
			if ldat, err := list.FindByType("ldat"); err == nil {
				raw, _ = ldat.Data.([]byte)
			}
		}
		pts := make([][2]float64, len(raw)/8)
		for i := range pts {
			nx, ny := f(raw[i*8:]), f(raw[i*8+4:])
			pts[i] = [2]float64{x0*(1-nx) + x1*nx, y0*(1-ny) + y1*ny}
		}
		n := len(pts) / 3
		for j := 0; j < n; j++ {
			v, o, in := pts[3*j], pts[3*j+1], pts[(3*j-1+len(pts))%len(pts)]
			s.Vertices = append(s.Vertices, v)
			s.OutTangents = append(s.OutTangents, [2]float64{o[0] - v[0], o[1] - v[1]})
			s.InTangents = append(s.InTangents, [2]float64{in[0] - v[0], in[1] - v[1]})
		}
		out = append(out, s)
	}
	return out
}
