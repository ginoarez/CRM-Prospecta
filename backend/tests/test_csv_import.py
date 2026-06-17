import io


def test_import_csv_creates_and_reports(client, auth_headers):
    csv_data = (
        "business_name,city,country,phone\n"
        "Gym A,Bogota,CO,3001234567\n"
        ",Bogota,CO,3001234567\n"            # missing business_name -> error row
        "Gym C,Lima,PE,not-a-phone\n"        # bad phone -> created, phone None
    )
    files = {"file": ("leads.csv", io.BytesIO(csv_data.encode()), "text/csv")}
    r = client.post("/leads/import-csv", files=files, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["created"] == 2
    assert len(body["errors"]) == 1
    assert body["errors"][0]["row"] == 2

    leads = client.get("/leads", headers=auth_headers).json()["items"]
    gym_c = next(l for l in leads if l["business_name"] == "Gym C")
    assert gym_c["phone"] is None
    assert gym_c["source"] == "csv"
