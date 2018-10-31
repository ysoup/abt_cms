def filter_char(content_text):
    content_text = content_text.replace("<p>", "")
    content_text = content_text.replace("</p>", "")
    content_text = content_text.replace("<br />", "")
    content_text = content_text.replace("<br/>", "")
    content_text = content_text.replace("&lsquo;", "‘")
    content_text = content_text.replace("&rsquo;", "’")
    content_text = content_text.replace("&ldquo;", "“")
    content_text = content_text.replace("&rdquo;", "”")
    content_text = content_text.replace("&circ;", "ˆ")
    content_text = content_text.replace("&middot;", "·")
    content_text = content_text.replace("&uml;", "¨")
    content_text = content_text.replace("&hellip;", "…")
    content_text = content_text.replace("&cedil;", "¸")
    content_text = content_text.replace("&acute;", "´")
    content_text = content_text.replace("&mdash;", "—")
    content_text = content_text.replace("&iexcl;", "¡")
    content_text = content_text.replace("&iquest;", "¿")
    content_text = content_text.replace("&amp;", "&")
    content_text = content_text.replace("&macr;", "¯")
    content_text = content_text.replace("&tilde;", "˜ ")
    content_text = content_text.replace("&lt;", "<")
    content_text = content_text.replace("&gt;", ">")
    content_text = content_text.replace("&shy;", "-")
    content_text = content_text.replace("&lsaquo;", "‹")
    content_text = content_text.replace("&rsaquo;", "›")

    return content_text
