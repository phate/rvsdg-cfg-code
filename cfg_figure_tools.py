import figure

def make_node(label, style = figure.base.THICK):
	return figure.base.make_text_box(label, canvas = cv, style = style)

def make_edge(origin, target, origin_rel = 0.5, target_rel = 0.5, origin_y = 1, target_y = 0, origin_label = None, origin_label_orient = 0, style = figure.base.SOLID, intermediate_stops = []):
	e = figure.base.connector_line([(origin, origin_rel, origin_y)] + intermediate_stops + [(target, target_rel, target_y)], style = style, canvas = cv)
	if origin_label:
		w = figure.base.label(origin_label, canvas = cv)
		a = figure.base.attach_layout(w, origin, origin_rel, origin_y, origin_label_orient, +1 if origin_y else -1, canvas = cv)
	return e

