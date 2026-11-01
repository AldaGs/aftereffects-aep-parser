package main

import (
	"encoding/json"
	"strings"
	"testing"
)

func TestStrokeDashes(t *testing.T) {
	var shp ShapeItemDoc
	src := `{"type":"stroke","strokeWidth":4,"dashes":{"dash":14,"gap":10,"offset":{"expression":"time*-40"}}}`
	if err := json.Unmarshal([]byte(src), &shp); err != nil {
		t.Fatal(err)
	}
	g := &Generator{}
	writeShapeItem(g, "lyr", "grp", shp)
	out := g.sb.String()
	for _, want := range []string{
		".property('ADBE Vector Stroke Dashes')",
		"try { sh_dashp_",
		".addProperty('ADBE Vector Stroke Dash 1')",
		".addProperty('ADBE Vector Stroke Gap 1')",
		".addProperty('ADBE Vector Stroke Offset')",
		".setValue(14)",
		".setValue(10)",
		`.expression = "time*-40"`,
	} {
		if !strings.Contains(out, want) {
			t.Errorf("missing %q in:\n%s", want, out)
		}
	}
}
