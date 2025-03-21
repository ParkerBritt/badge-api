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

| **Parameter** | **Description** | **Example** |
|---------------|-----------------|-------------|
| **`label`**   | The text displayed on the badge (optional). | `label=Python` |
| **`icon`**    | The icon displayed next to the label (optional). Compatible with any SimpleIcons name. | `icon=python` |
| **`color`**   | The background color of the badge in hex format (optional, without `#`). | `color=FF4713` |



### Example Usage
<code>https:\/\/domain.com\/badge?label=python&icon=python&color=3776AB</code>
<img src="https://parkerbritt.com/badge?label=python&icon=python&color=3776AB" align="right">

<code>https:\/\/domain.com\/badge?label=C%2B%2B&icon=cpp&color=00599C</code>
<img src="https://parkerbritt.com/badge?label=C%2B%2B&icon=cpp&color=00599C" align="right">

<code>https:\/\/domain.com\/badge?label=houdini&icon=houdini&color=FF4713</code>
<img src="https://parkerbritt.com/badge?label=houdini&icon=houdini&color=FF4713" align="right">
