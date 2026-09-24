![FrameKit – Parametric frames for Autodesk Fusion](images/FrameKit-GitHub-Banner.png)

# FrameKit

[Deutsch](README.md) | **English**

FrameKit is a planned add-in for Autodesk Fusion that creates a bolted support frame or a simple transport cart from T-slot aluminum profiles using dialog inputs. A 3D centerline preview lets users inspect the design before generating components.

## Project status

The integration demo (**0.1.1**) is available in [`fusion_addin/FrameKit`](fusion_addin/FrameKit). It provides three dialog tabs, saved defaults, and a simple frame made from rectangular solid profiles, followed by an automatic fit of all visible geometry in the viewport. See the [demo installation and test guide](docu/demo_installation.md) (German) for setup and current verification status. The features below describe the planned full scope.

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

- [Change history](docu/timeline.md) (German) – implemented changes and current verification status.
- [Demo installation and testing](docu/demo_installation.md) (German) – dialog, icons, versioning, and Fusion integration checks.
- [Project plan](docu/projektplan_FrameKit.md) (German) – full requirements, design rules, implementation steps, and acceptance criteria.
- [Branding and graphic assets](images/README.md) – details about the logo, GitHub banner, and Fusion command icons.
- [German README](README.md) – German project overview.

## License

See [LICENSE](LICENSE) for the license terms.
