import yaml, re, sys
SCHEMA = {"required_keys": {"id","desc","score"}, "forbid": re.compile(r"(os\.|subprocess|open\()")}
def validate(path):
    rules = yaml.safe_load(open(path, encoding="utf-8"))
    for h in rules.get("hypotheses", []):
        assert SCHEMA["required_keys"].issubset(h.keys()), f"missing keys in {h.get('id')}"
        assert not SCHEMA["forbid"].search(h["score"]), f"forbidden in {h['id']}"
    print("OK")
if __name__ == "__main__": validate(sys.argv[1])




