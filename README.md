<h1 align="center">Badge Api</h1>

<div align="center">
  <a href="https://github.com/ParkerBritt?tab=repositories&q=&type=&language=python&sort="><img src="https://cards.parkerbritt.com/badge?label=python&icon=python&color=3776AB"></a>
   <a href="https://github.com/FastAPI/FastAPI"><img src="https://cards.parkerbritt.com/badge?label=FastAPI&icon=fastapi&color=009688"></a>
</div>

My personal web API for serving badges and github cards.
I created this project because I wasn't satisfied with the level of control I had with existing solutions.
Feel free to fork for your own use, although some things are currently hardcoded to me for convenience.

## API

| **Endpoint** | **Description** |
|--------------|-----------------------|
| [`/badge`](#badge) | A small pill badge with an icon and a label. |
| [`/button`](#button) | A button shaped card with centered text, for linking somewhere. |
| [`/repo`](#repo) | A card for one repo, with its description, stats and a background image. |
| [`/languages`](#languages) | A card ranking a user's most-used languages. |
| [`/streak`](#streak) | A card with a user's total, current and longest contribution streaks. |
| [`/terminal_hero`](#terminal_hero) | A terminal styled intro card with an ASCII portrait. |
| [`/image`](#image) | Any image, cropped to fill a card. |
| [`/divider`](#divider) | A section heading over a faint rule. |
| [`/spacer`](#spacer) | An empty SVG, for pushing things apart. |
| [`/jenkins_badge`](#jenkins_badge) | A build status badge read from a Jenkins job. |


### badge

A small pill badge. Takes `label`, `icon` and `color`.

```
https://domain.com/badge?label=python&icon=python&color=3776AB
```

<table>
<tr><td width="800"><br><div align="center"><img src="https://cards.parkerbritt.com/badge?label=python&icon=python&color=3776AB"></div><br></td></tr>
</table>

```
https://domain.com/badge?label=C%2B%2B&icon=cpp&color=00599C
```

<table>
<tr><td width="800"><br><div align="center"><img src="https://cards.parkerbritt.com/badge?label=C%2B%2B&icon=cpp&color=00599C"></div><br></td></tr>
</table>

```
https://domain.com/badge?label=houdini&icon=houdini&color=FF4713
```

<table>
<tr><td width="800"><br><div align="center"><img src="https://cards.parkerbritt.com/badge?label=houdini&icon=houdini&color=FF4713"></div><br></td></tr>
</table>

### button

A button to link somewhere. Takes `label`, `icon`, `color`, `border_color`, `text_color`,
`border_radius` and `height`. If you leave the two extra colors off and they're worked out from `color`.

```
https://domain.com/button?label=Repos&icon=github
```

<table>
<tr><td width="800"><br><div align="center"><img src="https://cards.parkerbritt.com/button?label=Repos&icon=github"></div><br></td></tr>
</table>

```
https://domain.com/button?label=Website&icon=house
```

<table>
<tr><td width="800"><br><div align="center"><img src="https://cards.parkerbritt.com/button?label=Website&icon=house"></div><br></td></tr>
</table>

### repo

One repo's name, description and stats. Takes `repo` and optionally `user`, `title` and
`image_url`. With no `image_url` the card looks for `.github/thumbnail.png` in the repo itself.

```
https://domain.com/repo?title=Enzo&repo=enzo
```

<table>
<tr><td width="800"><br><div align="center"><img width="421" src="https://cards.parkerbritt.com/repo?title=Enzo&repo=enzo"></div><br></td></tr>
</table>

### languages

A user's top six languages. Takes `user`.

```
https://domain.com/languages
```

<table>
<tr><td width="800"><br><div align="center"><img width="421" src="https://cards.parkerbritt.com/languages"></div><br></td></tr>
</table>

### streak

Total, current and longest contribution streaks. Takes `user`.

```
https://domain.com/streak
```

<table>
<tr><td width="800"><br><div align="center"><img width="421" src="https://cards.parkerbritt.com/streak"></div><br></td></tr>
</table>

### terminal_hero

An about me themed as a terminal window, taking `name`, `username`, `role`, `stack`, `uptime`, `contact`, `terminal_title` and `command`.

```
https://domain.com/terminal_hero
```

<table>
<tr><td width="800"><br><div align="center"><img src="https://cards.parkerbritt.com/terminal_hero"></div><br></td></tr>
</table>

### image

Any image, cropped to fill a card. Takes `image_url`, `width` and `height`.

```
https://domain.com/image?height=140&image_url=https://github.com/user-attachments/assets/0c0b427b-b0b9-41fe-9e90-f3af80012890
```

<table>
<tr><td width="800"><br><div align="center"><img width="421" src="https://cards.parkerbritt.com/image?height=140&image_url=https://github.com/user-attachments/assets/0c0b427b-b0b9-41fe-9e90-f3af80012890"></div><br></td></tr>
</table>

### divider

A section heading. Takes `label` and `line_length`.

```
https://domain.com/divider?label=01+-+Currently+Working+On&line_length=300
```

<table>
<tr><td width="800"><br><div align="center"><img src="https://cards.parkerbritt.com/divider?label=01+-+Currently+Working+On&line_length=300"></div><br></td></tr>
</table>

### spacer

An empty SVG for pushing things apart. Takes `width` and `height`.

```
https://domain.com/spacer?width=40&height=20
```

This example splits the two cards.

<table>
<tr><td width="800"><br><div align="center"><img src="https://cards.parkerbritt.com/badge?label=python&icon=python&color=3776AB"><img src="https://cards.parkerbritt.com/spacer?width=40&height=20"><img src="https://cards.parkerbritt.com/badge?label=houdini&icon=houdini&color=FF4713"></div><br></td></tr>
</table>

### jenkins_badge

A passing or failing badge for a job on the Jenkins server named in `conf.env`. Takes `job` and
`build`, where `build` defaults to `lastBuild`.

```
https://domain.com/jenkins_badge?job=my-project
```

## Hosting

Using docker:

```bash
cp conf-example.env conf.env  # then fill it in
docker compose up --build
```

That serves the API on port `8005`.

Dev:
```bash
pip install -r requirements.txt
fastapi dev src/main.py
```


### Configuration

`conf.env` can be used to configure the program.

| **Variable** | **Description** |
|--------------|-------------------|
| `GITHUB_TOKEN` | A personal access token. Without one you'll likely hit github rate limiting. |
| `DEFAULT_USER` | The user used when no `user` is given. |
| `JENKINS_IP`, `JENKINS_PORT` | Where `/jenkins_badge` looks for Jenkins. |
