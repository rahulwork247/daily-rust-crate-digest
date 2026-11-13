import json, pathlib, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

URL = "https://crates.io/api/v1/crates?page=1&per_page=30&sort=new"
USER_AGENT = "daily-rust-crate-digest/1.0 (contact@rahulwork.dev)"

def run():
    req = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    crates = data.get("crates", [])
    
    # 1. feed.json
    items = [{"name": c.get("name"), "version": c.get("max_version", "1.0.0"), "description": c.get("description") or "", "url": f"https://crates.io/crates/{c.get('name')}", "created_at": c.get("created_at")} for c in crates]
    pathlib.Path("feed.json").write_text(json.dumps({"updated": datetime.now(timezone.utc).isoformat(), "items": items}, indent=2), encoding="utf-8")
    
    # 2. feed.xml (RSS)
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Daily Rust Crate Digest"
    ET.SubElement(channel, "link").text = "https://rahulwork247.github.io/daily-rust-crate-digest/"
    ET.SubElement(channel, "description").text = "Daily Rust crate digest"
    for c in crates:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = c.get("name", "")
        ET.SubElement(item, "link").text = f"https://crates.io/crates/{c.get('name')}"
        ET.SubElement(item, "description").text = c.get("description") or ""
    ET.ElementTree(rss).write("feed.xml", encoding="utf-8", xml_declaration=True)
    print("Feeds updated successfully.")

if __name__ == "__main__":
    run()
