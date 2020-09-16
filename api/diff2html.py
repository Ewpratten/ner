
def diff_prettyHtml(diff):
    html = []
    for line in diff.split("\n"):
        text = (line.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;").replace("\n", "&para;<br>"))
        if len(text) >= 3 and text[0] == text[1] == text[2]: 
            if text[0] == "+" :
                html.append("<span style=\"background:#e6ffe6;width:100%%;\">%s</span>" % text)
            elif text[0] == "-" :
                html.append("<span style=\"background:#ffe6e6;width:100%%;\">%s</span>" % text)
        elif len(text) >= 3 and text[0] == text[1] == "@": 
            html.append("<span style=\"background:#e6ebff;width:100%%;\">%s</span>" % text)
        elif len(text) >= 1: 
            if text[0] == "+" :
                html.append("<span style=\"color:green;width:100%%;\">%s</span>" % text)
            elif text[0] == "-" :
                html.append("<span style=\"color:red;width:100%%;\">%s</span>" % text)
            elif text[0] == " ":
                html.append("<span>%s</span>" % text)
            else:
                html.append("<span><strong>%s</strong></span>" % text)
        
    return "\n"+"\n".join(html)