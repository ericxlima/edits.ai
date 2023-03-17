# RiveSong

- Before run
```py
# add 
if 'reelShelfRenderer' in video_details:
    continue
if "showingResultsForRenderer" in video_details:
    continue
# in below line 150 of pytube/contrib/search.py 
```
```py
# In the file pytube/parser.py
# change this line 
[152]: func_regex = re.compile(r"function\([^)]+\)")
# to this
[152]: func_regex = re.compile(r"function\([^)]*\)")
```
```py
# in pytube/cipher.py modify this line
transform_plan_raw = find_object_from_startpoint(raw_code, match.span()[1] - 1)
# for this
transform_plan_raw = js
```
- Reqs

[imagemagick](https://imagemagick.org/)


