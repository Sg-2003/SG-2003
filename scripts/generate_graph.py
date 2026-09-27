import urllib.request
import re
from datetime import datetime

def generate_activity_svg(output_path="activity-graph.svg"):
    # 1. Fetch contributions from GitHub public calendar
    url = "https://github.com/users/Sg-2003/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    html = urllib.request.urlopen(req).read().decode("utf-8")

    days_raw = re.findall(r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="contribution-day-component-([^"]+)"', html)
    tds = {cid: dt for dt, cid in days_raw}

    tooltips_raw = re.findall(r'<tool-tip[^>]*for="contribution-day-component-([^"]+)"[^>]*>(.*?)</tool-tip>', html)
    tooltips = {}
    for cid, text in tooltips_raw:
        m = re.search(r'(\d+|No)\s+contribution', text)
        if m:
            cnt_str = m.group(1)
            tooltips[cid] = 0 if cnt_str == "No" else int(cnt_str)
        else:
            tooltips[cid] = 0

    data = []
    for cid, dt in tds.items():
        cnt = tooltips.get(cid, 0)
        data.append((dt, cnt))

    data.sort(key=lambda x: x[0])
    
    # Take last 31 days
    last_31 = data[-31:]
    if not last_31:
        print("Warning: No contribution days parsed.")
        return

    width = 860
    height = 300
    padding_top = 80
    padding_bottom = 45
    padding_left = 65
    padding_right = 35

    plot_width = width - padding_left - padding_right
    plot_height = height - padding_top - padding_bottom

    max_val = max(c for _, c in last_31)
    if max_val < 4:
        max_val = 4
    y_max = max_val + (1 if max_val % 2 != 0 else 0)
    y_steps = 4
    y_step_val = y_max / y_steps

    points = []
    n = len(last_31)
    for i, (dt, cnt) in enumerate(last_31):
        x = padding_left + (i / (n - 1)) * plot_width
        y = padding_top + plot_height - (cnt / y_max) * plot_height
        day_num = dt.split("-")[2].lstrip("0")
        points.append((x, y, cnt, day_num, dt))

    path_d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for pt in points[1:]:
        path_d += f" L {pt[0]:.1f} {pt[1]:.1f}"

    area_d = f"M {points[0][0]:.1f} {padding_top + plot_height:.1f}"
    for pt in points:
        area_d += f" L {pt[0]:.1f} {pt[1]:.1f}"
    area_d += f" L {points[-1][0]:.1f} {padding_top + plot_height:.1f} Z"

    y_grid_lines = []
    for s in range(y_steps + 1):
        val = int(s * y_step_val)
        y = padding_top + plot_height - (val / y_max) * plot_height
        y_grid_lines.append(f'<line class="ct-grid" x1="{padding_left}" y1="{y:.1f}" x2="{width - padding_right}" y2="{y:.1f}"/>')
        y_grid_lines.append(f'<text class="ct-label ct-vertical" x="{padding_left - 12}" y="{y + 4:.1f}" text-anchor="end">{val}</text>')

    x_grid_lines = []
    for i, (x, y, cnt, day_num, dt) in enumerate(points):
        x_grid_lines.append(f'<line class="ct-grid" x1="{x:.1f}" y1="{padding_top}" x2="{x:.1f}" y2="{padding_top + plot_height}"/>')
        x_grid_lines.append(f'<text class="ct-label ct-horizontal" x="{x:.1f}" y="{padding_top + plot_height + 20}" text-anchor="middle">{day_num}</text>')

    points_svg = []
    for x, y, cnt, day_num, dt in points:
        points_svg.append(f'<circle class="ct-point" cx="{x:.1f}" cy="{y:.1f}" r="4"><title>{cnt} contributions on {dt}</title></circle>')

    svg_content = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#58a6ff" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#58a6ff" stop-opacity="0.02"/>
    </linearGradient>
  </defs>

  <style>
    .card-bg {{
      fill: #0d1117;
      stroke: #30363d;
      stroke-width: 1px;
      rx: 6px;
    }}
    .title {{
      font: 600 18px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      fill: #58a6ff;
      text-anchor: middle;
    }}
    .axis-title {{
      font: 500 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      fill: #79c0ff;
      opacity: 0.8;
    }}
    .ct-label {{
      font: 400 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      fill: #8b949e;
    }}
    .ct-grid {{
      stroke: #30363d;
      stroke-width: 1px;
      stroke-dasharray: 2px 2px;
      opacity: 0.6;
    }}
    .ct-area {{
      fill: url(#areaGradient);
    }}
    .ct-line {{
      stroke: #79c0ff;
      stroke-width: 3px;
      fill: none;
      stroke-linecap: round;
      stroke-linejoin: round;
      stroke-dasharray: 4000;
      stroke-dashoffset: 4000;
      animation: dash 2.5s ease-out forwards;
    }}
    .ct-point {{
      fill: #58a6ff;
      stroke: #0d1117;
      stroke-width: 2px;
      transition: r 0.2s ease, fill 0.2s ease;
      cursor: pointer;
    }}
    .ct-point:hover {{
      r: 7px;
      fill: #79c0ff;
    }}
    @keyframes dash {{
      to {{
        stroke-dashoffset: 0;
      }}
    }}
  </style>

  <!-- Background Card -->
  <rect class="card-bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}"/>

  <!-- Title -->
  <text class="title" x="{width / 2}" y="38">Sukumar's Contribution Activity (Last 31 Days)</text>

  <!-- Axis Titles -->
  <text class="axis-title" x="{padding_left}" y="65">Contributions</text>
  <text class="axis-title" x="{width - padding_right}" y="{padding_top + plot_height + 40}" text-anchor="end">Days (Last 31 Days)</text>

  <!-- Grid lines -->
  <g class="grids">
    {' '.join(y_grid_lines)}
    {' '.join(x_grid_lines)}
  </g>

  <!-- Area Fill -->
  <path class="ct-area" d="{area_d}"/>

  <!-- Line Chart -->
  <path class="ct-line" d="{path_d}"/>

  <!-- Data Points -->
  <g class="points">
    {' '.join(points_svg)}
  </g>
</svg>
'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {output_path} ({len(svg_content)} bytes)")

if __name__ == "__main__":
    generate_activity_svg("activity-graph.svg")
