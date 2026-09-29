from backend.app.scrapers.html_cleaner import HTMLCleaner


def test_removes_scripts_and_styles():

    html = """
    <html>
        <head>
            <style>
                body { color: red; }
            </style>
        </head>

        <body>
            <h1>Equinor ASA</h1>

            <script>
                console.log("remove me");
            </script>

            <p>Energy company headquartered in Norway.</p>
        </body>
    </html>
    """

    cleaner = HTMLCleaner()

    result = cleaner.clean(html)

    assert "Equinor ASA" in result
    assert "Energy company headquartered in Norway." in result

    assert "console.log" not in result
    assert "color: red" not in result


def test_removes_navigation_and_footer():

    html = """
    <html>
        <body>

            <nav>
                Home About Contact
            </nav>

            <main>
                <h1>Company Information</h1>
                <p>This is the useful company content.</p>
            </main>

            <footer>
                Copyright 2026
            </footer>

        </body>
    </html>
    """

    cleaner = HTMLCleaner()

    result = cleaner.clean(html)

    assert "Company Information" in result
    assert "useful company content" in result

    assert "Home About Contact" not in result
    assert "Copyright 2026" not in result


def test_prefers_main_content():

    html = """
    <html>
        <body>

            <div>
                Unimportant website content
            </div>

            <main>
                <h1>Actual Company Information</h1>
                <p>Equinor operates in the energy industry.</p>
            </main>

        </body>
    </html>
    """

    cleaner = HTMLCleaner()

    result = cleaner.clean(html)

    assert "Actual Company Information" in result
    assert "Equinor operates in the energy industry." in result


def test_empty_html_returns_empty_string():

    cleaner = HTMLCleaner()

    assert cleaner.clean("") == ""
    assert cleaner.clean("   ") == ""


def test_whitespace_is_normalized():

    html = """
    <html>
        <body>
            <p>
                Equinor
                operates
                in Norway.
            </p>
        </body>
    </html>
    """

    cleaner = HTMLCleaner()

    result = cleaner.clean(html)

    assert result == "Equinor operates in Norway."