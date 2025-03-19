<h1 align="center">Badge Api</h1>

<div align="center">
  <a href="https://github.com/ParkerBritt?tab=repositories&q=&type=&language=python&sort="><img src="https://parkerbritt.com/badge?label=python&icon=python&color=3776AB"></a>
   <a href="https://github.com/FastAPI/FastAPI"><img src="https://parkerbritt.com/badge?label=FastAPI&icon=fastapi&color=009688"></a>
</div>

My personal web API for serving badges.
Currently they display repo toolsets, but I plan to expand the functionality in the future.
I created this project because I wasn't satisfied with the level of control I had with existing solutions.
An example of the badges created can be seen above.

Any simple [simpleicon](https://simpleicons.org) should be compatible.

### Parameters

- **`label`** (optional) – The text displayed on the badge.  
  - Example: `label=Python`
- **`icon`** (optional) – The icon displayed next to the label.  
  - Example: `icon=python`  
  - Compatible with any [SimpleIcons](https://simpleicons.org/) name.
- **`color`** (optional) – The background color of the badge in hex format (without `#`).  
  - Example: `color=FF4713` (Bright Orange)

### Example Usage
```
https://parkerbritt.com/badge?label=python&icon=python&color=3776AB
```
will give you<br>
<img src="https://parkerbritt.com/badge?label=python&icon=python&color=3776AB">
