![FrameKit – Parametric frames for Autodesk Fusion](images/FrameKit-GitHub-Banner.png)

# FrameKit

[Deutsch](README.md) | **English**

FrameKit is a planned add-in for Autodesk Fusion that creates a bolted support frame or a simple transport cart from T-slot aluminum profiles using dialog inputs. A 3D centerline preview lets users inspect the design before generating components.

## Project status

The integration demo (**0.4.4**) is available in [`fusion_addin/FrameKit`](fusion_addin/FrameKit). It provides three dialog tabs, saved defaults, and a frame made from demo solid profiles or imported DXF sections with optional shelves, followed by an automatic fit of all visible geometry in the viewport. Feet and casters can be selected as cylindrical placeholders; custom entries can be saved and deleted. Each frame carries a panel; the top panel can also sit above the posts without corner cutouts. Shelf count, individual heights, and panel thickness are configurable; blank heights are spaced automatically. See the [demo installation and test guide](docu/demo_installation.md) (German) for setup and current verification status. The features below describe the planned full scope.

New in **0.3.0**: a local DXF profile library with import validation, dimension confirmation, selection and deletion. Square sections centered at the origin retain their grooves and cavities when extruded. See [Profile library and DXF import](docu/profilbibliothek_dxf.md) (German) for supported entities, storage and Fusion verification. Cross members and top panel mounting from 0.2.1 remain available.

New in **0.3.1 (S05)**: separate profile choices for posts, frames and cross members, per-level overrides, and rectangular DXF sections with quarter-turn rotation. Cut lengths, panel cutouts and shelf spacing use the actual section dimensions. See [Profiles by component group](docu/profile_je_bauteilgruppe.md) (German). Versions **0.2.0, 0.2.1 and 0.3.0** were tested successfully by the user on 26 September 2026; Version 0.3.1 was also confirmed working by the user on 26 September 2026.

New in **0.4.0 (S06)**: frame/cart presets, individual foot/caster choices at each corner, and accessory editing and duplication. Unequal support heights block creation. All collapsible dialog sections start closed, with a smaller initial window height. Accessories remain cylindrical placeholders with brake, adjustment and mounting properties. See [Frame type and accessories](docu/bauart_zubehoer.md) (German). Version 0.4.0 was confirmed working without errors by the user on 26 September 2026.

New in **0.4.1**: colored errors and warnings throughout the dialog; enabling the preview fits the complete frame, including accessory overhangs, into the viewport. Subsequent input changes preserve manual zoom. Connector rules are recorded for the next step. Fusion verification is pending. See [Dialog messages and preview](docu/dialoghinweise_vorschau.md) (German).

New in **0.4.3**: supplied 20/30/40 mm STEP brackets replace the triangular placeholders. One component per size is reused at multiple positions, aligned to the outer profile faces and grouped under **91 | Winkel** for visibility. Preview outlines show full-size mounting envelopes. Accessory errors also appear directly below the foot/caster selection. See [Brackets and verification](docu/winkel.md) (German); confirmed working in Fusion by the user on 2026-09-26.

New in **0.4.4**: corrected dialog refresh behavior to address caret movement while typing (reported: `600` appears as `006`). Unchanged field states and messages are no longer rewritten; input validation does not modify dialog controls. 110 local tests pass; confirmation in Fusion is pending.

## Screenshots

### Version 0.3.0

Tested successfully by the user on 26 September 2026. The screenshots show different input states.

Completed frame with DXF profiles, three panels and cylindrical support placeholders.

![FrameKit 0.3.0 – Completed frame with DXF profiles, three panels and cylindrical support placeholders.](images/screenshots/0.3.0/FrameKit_V0-3-0_-02.png)

<details>
<summary>More views from version 0.3.0</summary>

Assembly structure with colored components, cross members and transparent panels.

![FrameKit 0.3.0 – Assembly structure with colored components, cross members and transparent panels.](images/screenshots/0.3.0/FrameKit_V0-3-0_-01.png)

Centerline preview with panel surfaces, accessory outlines and cross-member controls.

![FrameKit 0.3.0 – Centerline preview with panel surfaces, accessory outlines and cross-member controls.](images/screenshots/0.3.0/FrameKit_V0-3-0_-03.png)

Creation dialog with panel mounting, per-level cross members and preview options.

![FrameKit 0.3.0 – Creation dialog with panel mounting, per-level cross members and preview options.](images/screenshots/0.3.0/FrameKit_V0-3-0_-05.png)

Settings with the saved 20 × 20 mm DXF profile and the accessory library.

![FrameKit 0.3.0 – Settings with the saved 20 × 20 mm DXF profile and the accessory library.](images/screenshots/0.3.0/FrameKit_V0-3-0_-04.png)

Historical import diagnostic: POINT rejection during testing. POINT entities and marked construction geometry are now skipped.

![FrameKit 0.3.0 – Historical import diagnostic: POINT rejection during testing. POINT entities and marked construction geometry are now skipped.](images/screenshots/0.3.0/FrameKit_V0-3-0_-00.png)

</details>

### Version 0.1.5

All images below belong to the **0.1.5** screenshot set. The dialogs show different input states and do not necessarily match the pictured frame. Screenshots from other versions are kept in separate sets; see the [screenshot filing guide](images/screenshots/README.md).

<!-- Screenshot set 0.1.5: Use only images from images/screenshots/0.1.5/. Group newer versions separately. -->

**Frame and interface:** An example with top-mounted panels, corner cutouts, and cylindrical foot/caster placeholders alongside the creation dialog.

![FrameKit 0.1.5 – Frame with shelf panels and creation dialog](images/screenshots/0.1.5/FrameKit_015_FrameErstellen.png)

<details>
<summary>More views from version 0.1.5: dialog, settings, assembly structure, and info</summary>

**Create frame:** Configure dimensions, profile size, accessories, and shelves. Leaving a height blank displays the automatically calculated shelf height.

![FrameKit 0.1.5 – Frame creation dialog](images/screenshots/0.1.5/FrameKit_015_FrameErstellenDialog.png)

**Manage settings:** Save personal defaults and create or delete custom foot/caster placeholders with a name, type, height, and diameter.

![FrameKit 0.1.5 – Settings and placeholder library](images/screenshots/0.1.5/FrameKit_015_Einstellungen.png)

**Assembly structure:** The Fusion browser separates posts, frames, shelf levels, and accessories. The connections group is reserved for future development.

![FrameKit 0.1.5 – Organized assembly in the Fusion browser](images/screenshots/0.1.5/FrameKit_015_BrowserStruktur.png)

**Info:** Version, FrameKit logo, and links to the website, source code, releases, and support.

![FrameKit 0.1.5 – Info tab with project links](images/screenshots/0.1.5/FrameKit_015_Info.png)

</details>

## Planned features

- **Frames and transport carts:** Four continuous corner posts, a top frame, and an optional bottom frame with bolted connections.
- **Configurable dimensions:** Length, width, and overall height, with shared or different profiles for posts and beams.
- **Shelves and crossmembers:** Shelf levels with panels and perimeter support frames; crossmembers are evenly spaced while accounting for their widths.
- **Feet and casters:** Fixed or adjustable feet, swivel casters with optional brakes, rigid casters, and retractable casters based on a reference type still to be selected.
- **Extensible profile library:** Custom DXF cross-sections with metadata such as manufacturer, series, part number, slot size, material, and compatible connector sets, without code changes. Import checks validate scale, closed contours, and internal voids.
- **3D preview and input validation:** Profile centerlines ending at the actual cut faces; invalid inputs prevent generation and produce clear explanations.
- **Structured Fusion assemblies:** Each profile becomes a separate component with a stable ID, descriptive name, component properties, and named timeline groups.
- **Saved configuration:** Frames can be reopened in the dialog and rebuilt in a controlled manner.
- **CSV export:** Grouped cut lists with profile, length, quantity, and component IDs, plus bills of materials including panels, feet, casters, and defined connector sets.

## Intended workflow

1. Choose the frame type and configure dimensions, profiles, shelves, crossmembers, and feet or casters.
2. Display the centerline preview and inspect the design.
3. Generate the frame as a structured Fusion assembly.
4. Edit the saved configuration and rebuild the frame when needed.
5. Export cut lists and bills of materials as CSV files.

The preview, component generation, and exported lists are intended to share the same calculated component data. Calculation logic will be separated from Fusion geometry generation.

## Design rules and first-version limitations

Length and width refer to the outer dimensions of the profile frame, excluding caster overhang. Overall height runs from the supporting surface to the defined top of the frame, including a top-mounted panel if present. Calculations account for profile cross-sections, panel thicknesses, accessory heights, and mounting clearances.

The first version is intended for straight profile cuts. The reference profile, connector sets, panel mounting arrangement, and retractable caster reference type must be specified before implementation.

- The dialog and saved configuration remain authoritative; manual layout sketch edits are not used as inputs.
- Manual changes to generated components are not preserved during a rebuild. Components not managed by the add-in remain untouched.
- External references to regenerated faces are not guaranteed.
- Connector quantities can only be fully included in the bill of materials when mounting and quantity rules are defined; missing assignments will be flagged.
- Structural load-capacity analysis is outside the scope. Crossmember spacing geometrically implements user inputs.

## Implementation milestones

1. **Initial prototype:** Reference profile, four posts, top frame, dialog, and centerline preview.
2. **Profile assembly:** DXF extrusion, naming, properties, and timeline groups.
3. **Shelves and crossmembers:** Levels, panels, and evenly spaced supports.
4. **Accessories:** Feet, casters, and specific connector sets.
5. **Project editing and export:** Configuration loading, controlled rebuilding, and CSV lists.
6. **Acceptance:** Checks in Fusion, example files, and installation and library documentation.

Targeted calculation tests and separate checks in Fusion are planned. These will verify dimensions, profile voids, agreement between preview and assembly, exported quantities, and reopening saved configurations.

Future extensions include additional frame shapes, custom crossmember positions, crossmember counts based on a maximum clear span, handles, diagonal braces, additional import formats, and cut optimization for stock bars.

## Documentation

- [Implementation roadmap and versions](docu/ablaufplan.md) (German) – editable plan and implementation status.
- [Preview and layout](docu/vorschau_layout.md) (German) – display options, orientation, and the fixed layout sketch introduced in 0.2.0.
- [Part data and assembly structure](docu/bauteildaten.md) (German) – stable IDs, properties, and the Fusion timeline from 0.1.5 onward.
- [Change history](docu/timeline.md) (German) – implemented changes and current verification status.
- [Demo installation and testing](docu/demo_installation.md) (German) – dialog, icons, versioning, and Fusion integration checks.
- [Project plan](docu/projektplan_FrameKit.md) (German) – full requirements, design rules, implementation steps, and acceptance criteria.
- [Branding and graphic assets](images/README.md) – details about the logo, GitHub banner, and Fusion command icons.
- [German README](README.md) – German project overview.

## License

See [LICENSE](LICENSE) for the license terms.
