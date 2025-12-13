SIDEBAR_TABS = [
    {
        "id": "Dashboard",
        "title": "Dashboard",
        "icon": "ti ti-apps",
        "links": [
            {"title": "Home", "url_name": "controller:dashboard"}
        ]
    },
    {
        "id": "Zones",
        "title": "Zones",
        "icon": "ti ti-building",
        "links": [
            {"title": "Zones", "url_name": "controller:zone-list"},
        ]
    },
    {
        "id": "Schedules",
        "title": "Schedules",
        "icon": "ti ti-calendar",
        "links": [
            {"title": "Schedules", "url_name": "controller:schedule_list"},
            {"title": "Grouped Schedules", "url_name": "controller:grouped_schedule_list",},
        ]
    },
]

def sidebar_tabs(request):
    """
    Provides sidebar tabs with is_active flags for tabs, links, and children.
    """
    if not request.user.is_authenticated:
        return {"SIDEBAR_TABS": []}

    tabs = []
    resolver_match = getattr(request, "resolver_match", None)
    current_url_name = resolver_match.url_name if resolver_match else None

    for tab in SIDEBAR_TABS:

        tab_copy = tab.copy()
        tab_copy["is_active"] = False

        links_copy = []
        for link in tab_copy.get("links", []):
            link_copy = link.copy()
            link_copy["is_active"] = False

            # Check if link itself matches
            if link.get("url_name") == current_url_name:
                link_copy["is_active"] = True
                tab_copy["is_active"] = True

            # Check children
            children_copy = []
            if link.get("children"):
                for child in link["children"]:
                    child_copy = child.copy()
                    child_copy["is_active"] = child.get("url_name") == current_url_name
                    if child_copy["is_active"]:
                        link_copy["is_active"] = True
                        tab_copy["is_active"] = True
                    children_copy.append(child_copy)
                link_copy["children"] = children_copy

            links_copy.append(link_copy)

        tab_copy["links"] = links_copy
        tabs.append(tab_copy)

    return {"SIDEBAR_TABS": tabs}
