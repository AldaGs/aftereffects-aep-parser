package aep

import (
	"strconv"
	"unicode/utf16"
)

// A minimal reader for the COS (PDF-object-syntax) dictionaries AE stores
// text documents in. Values come back as map[string]interface{} (dictionary,
// keys without the slash), []interface{} (array), float64, bool, string
// (decoded text) or nil.
type cosReader struct {
	b []byte
	i int
}

// parseCOS reads a text document: a bare run of /key value pairs with no
// enclosing << >>, returned as one dictionary.
func parseCOS(b []byte) interface{} {
	r := &cosReader{b: b}
	d := map[string]interface{}{}
	for {
		r.skip()
		if r.i >= len(r.b) {
			return d
		}
		k, ok := r.value().(cosName)
		if !ok {
			return d
		}
		d[string(k)] = r.value()
	}
}

func (r *cosReader) skip() {
	for r.i < len(r.b) {
		c := r.b[r.i]
		if c == '%' {
			for r.i < len(r.b) && r.b[r.i] != '\n' && r.b[r.i] != '\r' {
				r.i++
			}
		} else if c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == 0 || c == '\f' {
			r.i++
		} else {
			return
		}
	}
}

func (r *cosReader) value() interface{} {
	r.skip()
	if r.i >= len(r.b) {
		return nil
	}
	switch c := r.b[r.i]; {
	case c == '<' && r.i+1 < len(r.b) && r.b[r.i+1] == '<':
		r.i += 2
		d := map[string]interface{}{}
		for {
			r.skip()
			if r.i >= len(r.b) {
				return d
			}
			if r.b[r.i] == '>' {
				r.i += 2
				return d
			}
			k, ok := r.value().(cosName)
			if !ok {
				return d
			}
			d[string(k)] = r.value()
		}
	case c == '[':
		r.i++
		var a []interface{}
		for {
			r.skip()
			if r.i >= len(r.b) {
				return a
			}
			if r.b[r.i] == ']' {
				r.i++
				return a
			}
			a = append(a, r.value())
		}
	case c == '/':
		r.i++
		s := r.i
		for r.i < len(r.b) && !isCOSDelim(r.b[r.i]) {
			r.i++
		}
		return cosName(r.b[s:r.i])
	case c == '(':
		return r.str()
	default:
		s := r.i
		for r.i < len(r.b) && !isCOSDelim(r.b[r.i]) {
			r.i++
		}
		if r.i == s {
			r.i++ // an unexpected delimiter: step over it
			return nil
		}
		w := string(r.b[s:r.i])
		switch w {
		case "true":
			return true
		case "false":
			return false
		}
		if f, err := strconv.ParseFloat(w, 64); err == nil {
			return f
		}
		return nil
	}
}

type cosName string

func isCOSDelim(c byte) bool {
	switch c {
	case ' ', '\t', '\n', '\r', 0, '\f', '/', '[', ']', '<', '>', '(', ')', '%':
		return true
	}
	return false
}

// str reads a (...) literal: backslash escapes, balanced parentheses, and
// UTF-16BE when it starts with a byte-order mark.
func (r *cosReader) str() string {
	r.i++
	var raw []byte
	depth := 0
	for r.i < len(r.b) {
		c := r.b[r.i]
		r.i++
		if c == '\\' && r.i < len(r.b) {
			raw = append(raw, r.b[r.i])
			r.i++
			continue
		}
		if c == '(' {
			depth++
		} else if c == ')' {
			if depth == 0 {
				break
			}
			depth--
		}
		raw = append(raw, c)
	}
	if len(raw) >= 2 && raw[0] == 0xfe && raw[1] == 0xff {
		u := make([]uint16, 0, len(raw)/2)
		for k := 2; k+1 < len(raw); k += 2 {
			u = append(u, uint16(raw[k])<<8|uint16(raw[k+1]))
		}
		return string(utf16.Decode(u))
	}
	return string(raw)
}

// cosAt walks a parsed COS value by dictionary keys (strings) and array
// indices (ints), returning nil as soon as a step is missing.
func cosAt(v interface{}, path ...interface{}) interface{} {
	for _, p := range path {
		switch k := p.(type) {
		case string:
			d, ok := v.(map[string]interface{})
			if !ok {
				return nil
			}
			v = d[k]
		case int:
			a, ok := v.([]interface{})
			if !ok || k >= len(a) {
				return nil
			}
			v = a[k]
		}
	}
	return v
}
