from ipywidgets import widgets
from IPython.display import display

from davpx import DavProxy
from IpyApp import IpyApp, widget_property



class BenchmarkAl3Li(IpyApp):
    @widget_property
    def wJobPath    ():
        return widgets.Text(description='Job path', value='SPP1713Benchmarks/Al3Li/OP')

    @widget_property
    def wKappa():
        return widgets.FloatText(description='$\kappa$', value=0.01)

    @widget_property
    def wC11     ():
        return widgets.FloatText(description='$\mathbb{C}_{11}$',   value=107.11e9)

    @widget_property
    def wC12     ():
        return widgets.FloatText(description='$\mathbb{C}_{12}$',   value=62.86e9)

    @widget_property
    def wC44     ():
        return widgets.FloatText(description='$\mathbb{C}_{44}$',   value=28.47e9)

    @widget_property
    def wSubmit     (self):
        btn = widgets.Button(description='Submit & Start simulation' )
        btn.on_click(self.submit)
        return btn

    @widget_property
    def wConcStep():
        return widgets.IntText(description='Time step', value=10000)

    @widget_property
    def btn_plot_conc     (self):
        btn = widgets.Button(description='Plot concentration profile' )
        btn.on_click(self.plot_conc)
        return btn

    def showUI(self):
        vboxes = (
            [self.wJobPath],
            [self.wKappa,
             widgets.Label(value="Elasticity coefficient $\mathbb{C}$ of the matrix phase"),
             self.wC11, self.wC12, self.wC44,
             self.wSubmit ],
            [self.wConcStep, self.btn_plot_conc]
        )

        tab = self.create_Accordion(['Working folder', 'Benchmark parameters', 'Post-processing'], vboxes)
        display(tab)

    def submit(self, *args):
        params=self.get_widget_values()
        input_cont_el = TEMPLATE_ElasticityInput.format(**params)
        path_el = 'ElasticityInput.opi'
        oc_path_el = 'OP/ProjectInput/' + path_el

        with open(path_el, 'w') as f:
            f.write(input_cont_el)
        print('Simulation input file has been writen to {}'.format(path_el))

        oc=DavProxy()
        oc.set_token()

        oc_proj_base = self.wJobPath.value.strip(' /')
        oc_path_el   = oc_proj_base + '/' + oc_path_el
        redirect_url = 'https://condor.iehk.rwth-aachen.de/aixvipmap/index.php/apps/files/?dir=/{}'.format(oc_proj_base)

        try:
            oc.put(path_el,oc_path_el)
        except ValueError as e:
            print ('Error during uploading files: ', e)
            print ('Please make sure the folder exists in your home folder on AIXVIPMAP: %s' % oc_path_el)
        from IPython.core.display import display, HTML
        display(HTML('Please open the <a href="{}">Job folder</a> in a new window.'.format(redirect_url)))

    def plot_conc(self, *args):
        import mayavi, vtk, os
        from mayavi import mlab
        mlab.init_notebook()

        from mayavi.sources.vtk_xml_file_reader import VTKXMLFileReader
        from mayavi.sources.vrml_importer import VRMLImporter
        from mayavi.modules.outline import Outline
        from mayavi.modules.streamline import Streamline
        from mayavi.modules.iso_surface import IsoSurface
        from mayavi.sources.vtk_file_reader import VTKFileReader

        print('Mayavi {}, {}, DISPLAY {}'.format(mayavi.__version__, vtk.vtkVersion.GetVTKSourceVersion(), os.environ['DISPLAY']))
        

        # fetch the results
        
        fname='Composition_{0:08d}.vtk'.format(self.wConcStep.value)
        oc_proj_base = self.wJobPath.value.strip(' /')

        oc=DavProxy()
        oc.set_token()
        oc.get(oc_proj_base + '/OP/VTK/'+fname, './' + fname)
        
        print('File ', fname, 'is successfully fetched.')
        # run mlab pipeline
        
        
        
        mlab.clf() # clear figure
        r = VTKFileReader()
        r.initialize(fname)
        r.point_scalars_name = 'TotalComposition_Li'
        
        scp=mlab.pipeline.scalar_cut_plane(r, view_controls=False,plane_orientation='y_axes')
        scpx=mlab.pipeline.scalar_cut_plane(r, view_controls=False,plane_orientation='x_axes')
        mlab.pipeline.outline(r)
        col_cp=mlab.scalarbar(scp, title='C(Li)', orientation='vertical')
        display(mlab.gcf())  # plot

TEMPLATE_ElasticityInput="""
Mechstate 0: Free boundaries
MechState 1: Applied Strain
MechState 2: Applied Stress
MechState 3: Mixed Stress / Strain

$MechState  Mechanical State: 2

$Comp_0   Name of the component               : Li

$CREF_Li_0      Reference concentration     : 0
$CREF_Li_1      Reference concentration     : 25

$Phase 0
$C11 {wC11}    {wKappa}
$C12 {wC12}    {wKappa}
$C13 {wC12}    {wKappa}
$C22 {wC11}    {wKappa}
$C23 {wC12}    {wKappa}
$C33 {wC11}    {wKappa}
$C44 {wC44}    {wKappa}
$C55 {wC44}    {wKappa}
$C66 {wC44}    {wKappa}

$E1 0   0
$E2 0   0
$E3 0   0
$E4 0   0
$E5 0   0
$E6 0   0

$Phase 1
$C11 139.8e9    0.0
$C12 33.7e9     0.0
$C13 33.7e9     0.0
$C22 139.8e9    0.0
$C23 33.7e9     0.0
$C33 139.8e9    0.0
$C44 40.7e9     0.0
$C55 40.7e9     0.0
$C66 40.7e9     0.0

$E1 -0.00975     0
$E2 -0.00975     0
$E3 -0.00975     0
$E4 0            0
$E5 0            0
$E6 0            0
"""
