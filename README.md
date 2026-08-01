<h1 align="center">Badge Api</h1>

<div align="center">
  <a href="https://github.com/ParkerBritt?tab=repositories&q=&type=&language=python&sort="><img src="https://cards.parkerbritt.com/badge?label=python&icon=python&color=3776AB"></a>
   <a href="https://github.com/FastAPI/FastAPI"><img src="https://cards.parkerbritt.com/badge?label=FastAPI&icon=fastapi&color=009688"></a>
</div>

My personal web API for serving badges and github cards.
I created this project because I wasn't satisfied with the level of control I had with existing solutions.
Feel free to fork for your own use, although some things are currently hardcoded to me for convenience.
### Parameters

| **Parameter** | **Description** | **Example** |
|---------------|-----------------|-------------|
| **`label`**   | The text displayed on the badge (optional). | `label=Python` |
| **`icon`**    | The icon displayed next to the label (optional). Compatible with any [SimpleIcons](https://simpleicons.org) name. | `icon=python` |
| **`color`**   | The background color of the badge in hex format (optional, without `#`). | `color=FF4713` |



### Example Usage
<code>https:\/\/domain.com\/badge?label=python&icon=python&color=3776AB</code>
<img src="https://cards.parkerbritt.com/badge?label=python&icon=python&color=3776AB" align="right">

<code>https:\/\/domain.com\/badge?label=C%2B%2B&icon=cpp&color=00599C</code>
<img src="https://cards.parkerbritt.com/badge?label=C%2B%2B&icon=cpp&color=00599C" align="right">

<code>https:\/\/domain.com\/badge?label=houdini&icon=houdini&color=FF4713</code>
<img src="https://cards.parkerbritt.com/badge?label=houdini&icon=houdini&color=FF4713" align="right">

