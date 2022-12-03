import dash

scripts = {}

def addScripts(page, scriptsToAdd):
    for pg in dash.page_registry:
        if page == pg:
            scripts[dash.page_registry[pg]['path']] = scriptsToAdd