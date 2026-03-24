# XML import need to replace these special characters
def escape_xml(text: str) -> str:
    if text is None:
        return ""

    return (
        text.replace("&", "&amp;")   
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            # .replace('"', "&quot;")
            # .replace("'", "&apos;")
    )