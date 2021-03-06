from spack import *
import os
import glob

# working config lines for ompss 14.06 :
#./nanox-0.7/config.log:    $ ./configure --prefix=/usr/gapps/exmatex/ompss --with-mcc=/usr/gapps/exmatex/ompss/ --with-hwloc=/usr
#./mcxx-1.99.2/config.log:    $ ./configure --prefix=/usr/gapps/exmatex/ompss --with-nanox=/usr/gapps/exmatex/ompss --enable-ompss --with-mpi=/opt/mvapich2-intel-shmem-1.7 --enable-tl-openmp-profile --enable-tl-openmp-intel

class Ompss(Package):
    """OmpSs is an effort to integrate features from the StarSs
       programming model developed by BSC into a single programming
       model. In particular, our objective is to extend OpenMP with
       new directives to support asynchronous parallelism and
       heterogeneity (devices like GPUs). However, it can also be
       understood as new directives extending other accelerator based
       APIs like CUDA or OpenCL. Our OmpSs environment is built on top
       of our Mercurium compiler and Nanos++ runtime system."""
    homepage = "http://pm.bsc.es/"
    url      = "http://pm.bsc.es/sites/default/files/ftp/ompss/releases/ompss-14.06.tar.gz"
    version('14.06', '99be5dce74c0d7eea42636d26af47b4181ae2e11')

    # all dependencies are optional, really
    depends_on("mpi")
    #depends_on("openmp")
    depends_on("hwloc")
    depends_on("extrae")

    def install(self, spec, prefix):
        if 'openmpi' in spec:
            mpi = spec['openmpi']
        elif 'mpich' in spec:
            mpi = spec['mpich']
        elif 'mvapich' in spec:
            mpi = spec['mvapich']

        openmp_options = ["--enable-tl-openmp-profile"]
        if spec.satisfies('%intel'):
            openmp_options.append( "--enable-tl-openmp-intel" )

        os.chdir(glob.glob('./nanox-*').pop())
        configure("--prefix=%s" % prefix, "--with-mcc=%s" % prefix, "--with-extrae=%s" % spec['extrae'].prefix, "--with-hwloc=%s" % spec['hwloc'].prefix)
        make()
        make("install")

        os.chdir(glob.glob('../mcxx-*').pop())
        configure("--prefix=%s" % prefix, "--with-nanox=%s" % prefix, "--enable-ompss", "--with-mpi=%s" % mpi.prefix, *openmp_options)
        make()
        make("install")

