import requests

def test_get_response():
    url = "https://parkerbritt.com/badge?label=FastAPI&icon=fastapi&color=009688"
    expected_response = """

<svg
    width="95.81"
    height="28"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
>
    <defs>
        <linearGradient id="bg_grad" x1="20%" y1="0%" x2="80%" y2="100%">
            <stop offset="0%" stop-color="#009688" />
            <stop offset="100%" stop-color="#008275" />
        </linearGradient>

        <filter id="drop_shadow_1" width="120" height="120">
            <!-- Offset shadow -->
            <feOffset in="SourceAlpha" dx="2" dy="2" result="offsetOut" />
            <!-- Blur the shadow -->
            <feGaussianBlur in="offsetOut" stdDeviation="1.8" result="blurOut" />
            <!-- Set shadow color -->
            <feFlood flood-color="black" flood-opacity="0.3" result="colorOut" />
            <!-- Apply shadow color -->
            <feComposite in="colorOut" in2="blurOut" operator="in" result="shadow" />
            <!-- Merge shadow with original shape -->
            <feMerge>
                <feMergeNode in="shadow" />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>
    </defs>

    <rect x="0" y="0" width="95.81" height="28" fill="url(#bg_grad)" rx="8"/>
  
  
    <g transform="translate(9,7.0)" fill="white" filter="url(#drop_shadow_1)">  
        <svg role="img" width="14" height="14" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 .0387C5.3729.0384.0003 5.3931 0 11.9988c-.001 6.6066 5.372 11.9628 12 11.9625 6.628.0003 12.001-5.3559 12-11.9625-.0003-6.6057-5.3729-11.9604-12-11.96m-.829 5.4153h7.55l-7.5805 5.3284h5.1828L5.279 18.5436q2.9466-6.5444 5.892-13.0896"/>
        </svg>
    </g>
    <text
        x="32"
        y="15.0"
        font-family="monospace,Liberation Mono,Consolas,Menlo,Monaco,Lucida Console,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New,serif"
        font-size="13"
        fill="white"
        dominant-baseline="middle"
        text-rendering="geometricPrecision"
        font-weight="bold"
    >
        FASTAPI
    </text>
</svg>
"""
    response = requests.get(url)
    assert response.text.strip()==expected_response.strip()
