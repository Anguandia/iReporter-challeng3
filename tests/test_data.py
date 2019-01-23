dat = {
    "basic": {
        "location": "here", "createdBy": 1, "comment": "flooding",
        "title": "floods"},
    "optional": {"location": "there", "createdBy": 1, "comment": "flooding",
                 "type": "intervention flag", "title": "floods"},
    "resolved": {"location": "where", "createdBy": 1, "comment": "flooding",
                 "status": "resolved", "title": "floods"},
    "empty": {"location": "", "createdBy": 1, "comment": "flooding", "type":
              "intervention flag", "title": "floods"},
    "invalid": {"location": "here", "createdBy": "1", "comment": "flooding",
                "title": "floods"},
    "incomplete": {"location": "here", "createdBy": 1},
    "invalidComment": {"location": "here", "comment": "9", "createdBy": 1,
                       "title": "floods"},
    "video": {
        "location": "here", "createdBy": 1, "comment": "flooding",
        "title": "floods", "images": [
            "http://google.com/images/cat.jpeg", 256,
            "file/images/desert.jpeg"]},
    'bad_coord': {'location': 'three,thirty'},
    'gud_coord': {'location': '03,31'}
}
