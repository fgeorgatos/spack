from spack import *

class Extrae(Package):
    """Extrae is the package devoted to generate tracefiles which can
       be analyzed later by Paraver. Extrae is a tool that uses
       different interposition mechanisms to inject probes into the
       target application so as to gather information regarding the
       application performance. The Extrae instrumentation package can
       instrument the MPI programin model, and the following parallel
       programming models either alone or in conjunction with MPI :
       OpenMP, CUDA, OpenCL, pthread, OmpSs"""
    homepage = "http://www.bsc.es/computer-sciences/extrae"
    url      = "http://www.bsc.es/ssl/apps/performanceTools/files/extrae-2.5.1.tar.bz2"
    version('2.5.1', '422376b9c68243bd36a8a73fa62de106')

    #depends_on("mpi")
    depends_on("openmpi@:1.6")
    depends_on("dyninst")
    depends_on("libunwind")
    depends_on("boost")
    depends_on("libdwarf")
    depends_on("papi")

    def install(self, spec, prefix):
        if 'openmpi' in spec:
            mpi = spec['openmpi']
            #if spec.satisfies('@2.5.1') and spec.satisfies('^openmpi@1.6.5'):
            #    tty.error("Some headers conflict when using OpenMPI 1.6.5. Please use 1.6 instead.")
        elif 'mpich' in spec:
            mpi = spec['mpich']
        elif 'mvapich2' in spec:
            mpi = spec['mvapich2']

        configure("--prefix=%s" % prefix,
                  "--with-mpi=%s" % mpi.prefix,
                  "--with-unwind=%s" % spec['libunwind'].prefix,
                  "--with-dyninst=%s" % spec['dyninst'].prefix,
                  "--with-boost=%s" % spec['boost'].prefix,
                  "--with-dwarf=%s" % spec['libdwarf'].prefix,
                  "--with-papi=%s" % spec['papi'].prefix,
                  "--with-dyninst-headers=%s" % spec['dyninst'].prefix.include,
                  "--with-dyninst-libs=%s" % spec['dyninst'].prefix.lib)

        make()
        make("install", parallel=False)

