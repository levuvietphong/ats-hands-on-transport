"""Module containing functions for visualizing and processing mesh data from ATS"""

import numpy as np
import geopandas as gpd
import h5py
from pyproj.crs import CRS
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Polygon  # Use this instead of PolygonPatch
import shapely
import colorcet as cc
import pyvista as pv
import vtk
vtk.vtkObject.GlobalWarningDisplayOff()


def daymet_crs():
    """Returns the CRS used by DayMet files, but in m, not km.

    Returns
    -------
    out : crs-type
        The DayMet CRS.  The user should not care what this is.

    """
    # old proj: return from_string('+proj=lcc +lat_1=25 +lat_2=60 +lat_0=42.5 +lon_0=-100 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs ')
    # new proj...
    return CRS.from_string(
        '+proj=lcc +lat_1=25 +lat_2=60 +lat_0=42.5 +lon_0=-100 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs'
    )


def GetMeshPolygons(mfile=None):
    """This functions read mesh from h5 files
    
    Returns
    -------
    polygons:
        List of element in polygon format

    """
    # Read mesh file to extract the coordinates of the nodes
    fn = h5py.File(mfile, 'r')

    # Get group info
    group = fn["/0"]
    node_coor = group['Mesh']['Nodes'][:]
    group['Mesh'].keys()
    elems_mixed = group['Mesh']['MixedElements'][:]
    num_elems = group['Mesh']['ElementMap'].shape[0]

    # Loop to extract the index of the nodes that form each element
    elem_type = np.zeros(num_elems)
    mesh_topology = np.zeros((num_elems, 5))
    for i in range(num_elems):
        elem_type[i] = elems_mixed[0]
        if elem_type[i] == 4:
            mesh_topology[i, 0:3] = elems_mixed[1:4].flatten()
            # Remove elements from elems_mixed
            elems_mixed = elems_mixed[4:]
        elif elem_type[i] == 5:
            mesh_topology[i, 0:4] = elems_mixed[1:5].flatten()
            # Remove elements from elems_mixed
            elems_mixed = elems_mixed[5:]
        elif elem_type[i] == 3:
            mesh_topology[i, 0:5] = elems_mixed[2:7].flatten()
            # Remove elements from elems_mixed
            elems_mixed = elems_mixed[7:]

    # Extract the unique nodes
    noodes_unique = np.unique(mesh_topology.flatten())

    # convert to integer
    noodes_unique = noodes_unique.astype(int)

    # Get node coordinates
    node_coors = node_coor[noodes_unique, :]

    polygons = []
    for i in range(mesh_topology.shape[0]):
        # Extract the coordinates of the nodes that form the element
        nodes = mesh_topology[i, :]

        # Replace by -1 the zeros in column 4 and 5. This is done since there are some elements with node id equal to zero
        nodes[-2:][nodes[-2:] == 0] = -1

        # Remove the -1
        nodes = nodes[nodes != -1]
        nodes_elem_coors = node_coor[nodes.astype(int), :]

        # Create a polygon
        polygon = shapely.geometry.Polygon(nodes_elem_coors)
        polygons.append(polygon)

    return polygons


def PlotPolygonsFields(polygons, field, cmap='jet', alpha=1, lw=1, edgecolor='k',
                       vmin=None, vmax=None, label=None, colorbar=False, ax=None):
    """
    Plots Shapely polygons with colors based on the provided field values.
    """
    if len(polygons) != len(field):
        raise ValueError("Each polygon must correspond to a field value.")

    if vmin is None:
        vmin = min(field)
    if vmax is None:
        vmax = max(field)

    if ax is None:
        _, ax = plt.subplots()

    ax.set_aspect('equal')
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(cmap)

    patches = []

    for polygon, fieldval in zip(polygons, field):
        nodes = np.array(polygon.exterior.xy).T  # Get the exterior coordinates
        patch = Polygon(nodes, closed=True, alpha=alpha, linewidth=lw, edgecolor=edgecolor)
        patches.append(patch)
        patch.set_facecolor(cmap(norm(fieldval)))

    for patch in patches:
        ax.add_patch(patch)

    ax.set_axis_off()

    if colorbar:
        # Add colorbar if needed
        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.02)
        
        # Make colorbar ticks smarter
        tick_locator = plt.MaxNLocator(nbins=5)
        cbar.locator = tick_locator
        cbar.update_ticks()
        if label:
            cbar.set_label(label)
    plt.tight_layout()


def get_skip_number(filename):
    """ Count the number of lines starting with '#' in a file """
    with open(filename, 'r') as site:
        return sum(1 for line in site if line.startswith('#'))


def get_cmap(name):
    """
    Returns a colormap based on the given variable name.

    Args:
        name (str): The name of the variable for which to get a colormap.

    Returns:
        matplotlib.colors.Colormap: The colormap object corresponding to the input name.
        If the name is not found in the predefined dictionary, it returns the 'jet' colormap as default.
    """
    cmap_dict = {
        'elevation': 'terrain',
        'ponded_depth': cc.cm.CET_CBL2_r,
        'surface_subsurface_flux': cc.cm.CET_R4
    }
    return cmap_dict.get(name, 'jet')


def get_boundary_polygons(surface_polys):
    gdf = gpd.GeoDataFrame(geometry=surface_polys)
    gdf.crs = daymet_crs()
    gdf_union = gdf.union_all()
    return gpd.GeoDataFrame(crs=gdf.crs, geometry=[gdf_union])


def plot_surface(variables, poly_surface, vis_surface, step, time, domain='surface',
                 vmin=None, vmax=None, cmap=None):
    """
    Plot surface variables on a mesh.

    Args:
        variables (list): List of variable names to plot.
        poly_surface (list): List of polygon geometries.
        vis_surface: Visualization data object.
        step (int): Time step index for data.
        vmin (list, optional): List of minimum values for color scaling.
        vmax (list, optional): List of maximum values for color scaling.
        cmap (list, optional): List of colormaps for each variable.
    """
    num_plots = len(variables)
    gdf_clip = get_boundary_polygons(poly_surface)

    _, ax = plt.subplots(1, num_plots, sharex=True, sharey=True, figsize=(4*num_plots, 6))
    plt.suptitle(f'Time: {time[step]/vis_surface.time_factor} {vis_surface.time_unit}', fontsize=16)
    for k, var in enumerate(variables):
        data = vis_surface.getArray(domain+'-'+var)[step, :]
        colormap = cmap[k] if cmap[k] is not None else get_cmap(var)
        cmin = vmin[k] if vmin is not None else None
        cmax = vmax[k] if vmax is not None else None

        if cmin is None:
            cmin = np.floor(np.nanmin(data))
        if cmax is None:
            cmax = np.ceil(np.nanmax(data))

        PlotPolygonsFields(poly_surface, data, cmap=colormap, vmin=cmin, vmax=cmax, lw=0.2,
                           ax=ax[k], colorbar=True)
        ax[k].set_title(var, y=0.95, fontsize=14)
        ax[k].set_axis_off()
        gdf_clip.plot(ax=ax[k], color="None", edgecolor='k', lw=1)


def plot_domain(variables, poly_surface, vis_domain, num_surface_elements, step, time, layer,
                vmin=None, vmax=None, cmap=None):
    """
    Plot domain variables on a mesh.

    Args:
        variables (list): List of variable names to plot.
        poly_surface (list): List of polygon geometries.
        vis_domain: Visualization data object.
        step (int): Time step index for data.
        vmin (list, optional): List of minimum values for color scaling.
        vmax (list, optional): List of maximum values for color scaling.
        cmap (list, optional): List of colormaps for each variable.
    """
    num_plots = len(variables)
    gdf_clip = get_boundary_polygons(poly_surface)
    num_steps = len(vis_domain.cycles)
    num_layers = int(np.shape(vis_domain.centroids)[0] / num_surface_elements)

    _, ax = plt.subplots(1, num_plots, sharex=True, sharey=True, figsize=(4*num_plots, 6))
    plt.suptitle(f'Time: {time[step]/vis_domain.time_factor} {vis_domain.time_unit}', fontsize=16)
    for k, var in enumerate(variables):
        data = vis_domain.getArray(var).reshape(num_steps, num_surface_elements, num_layers)[step, :, layer]
        colormap = cmap[k] if cmap is not None else get_cmap(var)
        cmin = vmin[k] if vmin is not None else None
        cmax = vmax[k] if vmax is not None else None

        if cmin is None:
            cmin = np.floor(np.nanmin(data))
        if cmax is None:
            cmax = np.ceil(np.nanmax(data))

        PlotPolygonsFields(poly_surface, data, cmap=colormap, vmin=cmin, vmax=cmax, lw=0.2,
                           ax=ax[k], colorbar=True)
        ax[k].set_title(var, y=0.95, fontsize=14)
        ax[k].set_axis_off()
        gdf_clip.plot(ax=ax[k], color="None", edgecolor='k', lw=1)


def load_mesh_exodus(mesh_file, z_scale=1.0):
    """
    Load and process an Exodus mesh file, applying optional z-axis scaling.

    Args:
        mesh_file (str): Path to the Exodus mesh file to load
        z_scale (float, optional): Scaling factor to apply to z-coordinates. Defaults to 1.0.

    Returns:
        pyvista.UnstructuredGrid: The processed mesh with scaled z-coordinates
    """
    mesh = pv.read(mesh_file)
    combined_mesh = mesh.combine()
    z_values = combined_mesh.points[:, 2]  # Z values are in the 3rd column
    combined_mesh["Z-values"] = z_values
    domain_mesh = combined_mesh.warp_by_scalar(scalars="Z-values", factor=z_scale)
    return domain_mesh


def toggle_pick_callback(point, plotter):
    """
    Toggle the visibility of a point label in the plotter.

    This function is used as a callback for point picking in a 3D visualization.
    It either adds a new label for a picked point or removes an existing label
    if the point has been picked before.

    Args:
        point (tuple): The 3D coordinates of the picked point.
        plotter: The plotter object used for visualization.

    Global Variables:
        picked_points_labels (dict): A dictionary to store point labels.
    """
    point_key = tuple(point)

    # Check if the point already has a label
    global picked_points_labels

    if 'picked_points_labels' not in globals():
        picked_points_labels = {}

    if point_key in picked_points_labels:
        # If it exists, remove the label
        plotter.remove_actor(picked_points_labels[point_key])
        del picked_points_labels[point_key]
    else:
        # Create a new label at the picked point
        label = plotter.add_point_labels(
            [point],
            [f"{point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f}"],
            font_size=12,
            point_color="red",
            text_color="white",
            fill_shape=True
        )
        # Store the label in the dictionary
        picked_points_labels[point_key] = label


def plot_mesh(domain_mesh, opacity=1, show_edges=True, show_scalar_bar=True, pickable=True,
              show_zlabels=False, cmap='viridis', show_toplayer=False, normal=None,
              window_size=None, link_views=True, view_isometric=False, set_background=True,
              lighting=False):
    """
    Plot a 3D mesh with interactive point picking capabilities.

    Args:
        domain_mesh: The PyVista mesh object to be plotted
        show_edges (bool, optional): Whether to display mesh edges. Defaults to True.
        show_scalar_bar (bool, optional): Whether to show the scalar bar. Defaults to True.
        pickable (bool, optional): Whether to enable point picking. Defaults to True.
        show_zlabels (bool, optional): Whether to show Z-axis labels. Defaults to False.
        window_size (list, optional): Window dimensions [width, height]. Defaults to [1200, 800].

    The function creates an interactive 3D visualization where users can:
    - Click points to toggle coordinate labels
    - View mesh edges if enabled
    - See elevation data via a scalar bar if enabled
    - Interact with the mesh using standard PyVista controls
    """
    if normal is None:
        normal = [0, 0, 1]

    if window_size is None:
        window_size = [640, 480]

    if show_toplayer:
        # toplayer_mesh = domain_mesh.slice(normal=normal)
        zmax = domain_mesh.bounds[5]  # Get maximum z-coordinate from mesh bounds
        toplayer_mesh = domain_mesh.extract_surface().project_points_to_plane(normal=normal)
        toplayer_mesh.points[:, 2] = zmax  # Set Z coordinates to match domain_mesh max height
        shape = (1, 2)
    else:
        shape = (1, 1)

    sargs = dict(height=0.25, vertical=True, position_x=0.05, position_y=0.05)

    pl = pv.Plotter(window_size=window_size, shape=shape)
    picked_points_labels = {}
    pl.add_mesh(
        domain_mesh,
        opacity=opacity,
        lighting=lighting,
        show_edges=show_edges,
        pickable=pickable,
        show_scalar_bar=show_scalar_bar,
        scalar_bar_args=sargs,
        cmap=cmap,
    )

    if show_toplayer:
        pl.subplot(0, 1)
        pl.add_mesh(
            toplayer_mesh,
            show_edges=show_edges,
            pickable=pickable,
            show_scalar_bar=True,
            color='white',
            smooth_shading=True,
        )

    # pl.add_scalar_bar(vertical=True, title="Elevation", n_labels=5)
    pl.enable_surface_point_picking(
        callback=lambda point: toggle_pick_callback(point, pl),
        show_point=False,
        picker='point',
    )

    pl.show_bounds(show_zlabels=show_zlabels)
    if link_views:
        pl.link_views()
    if view_isometric:
        pl.view_isometric()
    if set_background:
        pl.set_background("royalblue", top="aliceblue")

    pl.show()
