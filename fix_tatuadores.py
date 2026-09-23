from pathlib import Path
import re
import shutil

FILES = {
    "es": Path("Pages/es/desktop/tatuadores/index.html"),
    "en": Path("Pages/en-gb/desktop/tatuadores/index.html"),
}

def fix_file(path, lang):
    text = path.read_text(encoding="utf-8")

    # Backup
    backup = path.with_suffix(".index.html.backup")
    shutil.copy2(path, backup)

    # ---------------------------------------------------------
    # 1. Correct HTML language
    # ---------------------------------------------------------
    if lang == "en":
        text = re.sub(
            r'(<html\b[^>]*\blang=")[^"]+(")',
            r'\1en\2',
            text,
            count=1
        )
    else:
        text = re.sub(
            r'(<html\b[^>]*\blang=")[^"]+(")',
            r'\1es\2',
            text,
            count=1
        )

    # ---------------------------------------------------------
    # 2. Correct current-page ./ links
    # ---------------------------------------------------------
    if lang == "es":
        text = text.replace('href="./"', 'href="/tatuadores/"')
    else:
        text = text.replace('href="./"', 'href="/en-gb/tatuadores/"')

    # ---------------------------------------------------------
    # 3. Correct English non-language-selector links
    # ---------------------------------------------------------
    if lang == "en":

        # Home links without an explicit page alias
        text = text.replace(
            'href="/"',
            'href="/en-gb/home/"'
        )

        text = text.replace(
            'raw_url="/"',
            'raw_url="/en-gb/home/"'
        )

        # Normal navigation links
        replacements = {
            '/tatuadores/': '/en-gb/tatuadores/',
            '/el-estudio/': '/en-gb/el-estudio/',
            '/contacto/': '/en-gb/contacto/',
            '/blog/': '/en-gb/blog/',
        }

        # Only modify anchors that are NOT multilingual selectors.
        def fix_normal_anchor(match):
            attrs = match.group(1)

            if 'data-disable-ajax-navigation="true"' in attrs:
                return match.group(0)

            for old, new in replacements.items():
                attrs = attrs.replace(f'href="{old}"', f'href="{new}"')
                attrs = attrs.replace(f'raw_url="{old}"', f'raw_url="{new}"')

            return '<a' + attrs + '>'

        text = re.sub(
            r'<a\b([^>]*)>',
            fix_normal_anchor,
            text
        )

    # ---------------------------------------------------------
    # 4. Correct every multilingual language selector
    # ---------------------------------------------------------
    def fix_language_anchor(match):
        attrs = match.group(1)
        inner = match.group(2)

        is_english = 'alt="English"' in inner
        is_spanish = 'alt="Español"' in inner or 'alt="Espa&ntilde;ol"' in inner

        if not (is_english or is_spanish):
            return match.group(0)

        if lang == "en":
            if is_english:
                href = "/en-gb/tatuadores/"
                alias = "en-gb/tatuadores"
            else:
                href = "/tatuadores/"
                alias = "tatuadores"
        else:
            if is_spanish:
                href = "/tatuadores/"
                alias = "tatuadores"
            else:
                href = "/en-gb/tatuadores/"
                alias = "en-gb/tatuadores"

        attrs = re.sub(r'href="[^"]*"', f'href="{href}"', attrs, count=1)
        attrs = re.sub(r'raw_url="[^"]*"', f'raw_url="{href}"', attrs, count=1)
        attrs = re.sub(
            r'data-target-page-alias="[^"]*"',
            f'data-target-page-alias="{alias}"',
            attrs,
            count=1
        )

        return '<a' + attrs + '>' + inner + '</a>'

    text = re.sub(
        r'<a\b([^>]*data-disable-ajax-navigation="true"[^>]*)>([\s\S]*?</a>)',
        lambda m: fix_language_anchor(
            re.match(
                r'<a\b([^>]*)>([\s\S]*?)</a>',
                m.group(0)
            )
        ),
        text
    )

    # ---------------------------------------------------------
    # 5. Hide the desktop language widget on mobile.
    #
    # Tatuadores has a desktop multilingual widget and a
    # mobile multilingual widget. The desktop one was appearing
    # on mobile as the extra flag at the top.
    # ---------------------------------------------------------
    mobile_fix = """
<style id="tatuadores-mobile-language-fix">
@media (max-width: 767px) {
    #946d7a15 {
        display: none !important;
    }
}
</style>
"""

    if "tatuadores-mobile-language-fix" not in text:
        text = text.replace("</head>", mobile_fix + "\n</head>", 1)

    path.write_text(text, encoding="utf-8")

    print(f"FIXED: {path}")
    print(f"BACKUP: {backup}")


for lang, path in FILES.items():
    if not path.exists():
        print(f"NOT FOUND: {path}")
        continue

    fix_file(path, lang)

print("\nDONE.")
