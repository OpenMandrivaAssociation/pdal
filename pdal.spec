%define _disable_lto 1

%global libname	%mklibname %{name}
%global devname	%mklibname %{name} -d
%global major	16

# We don't want to provide private PDAL extension libs (to be verified)
%global __provides_exclude_from ^%{_libdir}/libpdal_plugin.*\.so.*$

%bcond_with doc

Summary:	Point Data Abstraction Library
Name:		pdal
Version:	2.6.2
Release:	1
Group:		Sciences/Geosciences
License:	BSD-3-Clause AND Apache-2.0 AND MIT AND BSL-1.0
URL:		https://www.pdal.io
Source:		https://github.com/%{name}/%{name}/releases/download/%{version}/PDAL-%{version}-src.tar.bz2
# (fedora)
Patch0:		pdal_unbundle.patch
Patch1:		pdal_tests.patch
Patch2:		PDAL_build.patch
Patch3:		pdal_bashcompletion.patch
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	boost-devel
BuildRequires:	hdf5-devel
BuildRequires:	pkgconfig(eigen3)
BuildRequires:	pkgconfig(gdal)
BuildRequires:	pkgconfig(geos)
BuildRequires:	pkgconfig(geotiff)
BuildRequires:	pkgconfig(gtest)
BuildRequires:	pkgconfig(jsoncpp)
BuildRequires:	pkgconfig(libpq)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(netcdf)
BuildRequires:	pkgconfig(proj)
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	python%{pyver}dist(breathe)
BuildRequires:	python%{pyver}dist(numpy)
%if %{with doc}
BuildRequires:	python%{pyver}dist(sphinx)
BuildRequires:	python%{pyver}dist(sphinxcontrib-bibtex)
BuildRequires:	python%{pyver}dist(sphinxcontrib-spelling)
BuildRequires:	python%{pyver}dist(sphinx-rtd-theme)
%endif
BuildRequires:	qhull-devel

Requires:	%{libname} = %{EVRD}
Requires:	bash-completion

%description
PDAL is a BSD licensed library for translating and manipulating point cloud
data of various formats. It is a library that is analogous to the GDAL raster
library. PDAL is focused on reading, writing, and translating point cloud
data from the ever-growing constellation of data formats. While PDAL is not
explicitly limited to working with LiDAR data formats, its wide format
coverage is in that domain.

PDAL is related to Point Cloud Library (PCL) in the sense that both work with
point data, but PDAL’s niche is data translation and processing pipelines, and
PCL’s is more in the algorithmic exploitation domain. There is cross over of
both niches, however, and PDAL provides a user the ability to exploit data
using PCL’s techniques.

%files
%{_bindir}/pdal
%{_datadir}/bash-completion/completions/pdal

#--------------------------------------------------------------------

%package -n %{libname}
Summary:	The shared libraries required for PDAL
Group:		System/Libraries

%description -n %{libname}
The pdal-libs package provides the essential shared libraries for any
PDAL client program or interface. You will need to install this package
to use PDAL

%files -n %{libname}
%license LICENSE.txt
%license vendor/arbiter/LICENSE
%license plugins/e57/libE57Format/LICENSE.md
#{_libdir}/libpdal_base.so.%{major}*
%{_libdir}/libpdalcpp.so.%{major}*
%{_libdir}/libpdal_plugin_kernel_fauxplugin.so.%{major}*
%{_libdir}/libpdal_plugin_reader_pgpointcloud.so.%{major}*
%{_libdir}/libpdal_plugin_writer_pgpointcloud.so.%{major}*
#{_libdir}/libpdal_util.so.%{major}*

#--------------------------------------------------------------------

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C++
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
The pdal-devel package contains the header files and libraries needed to
compile C or C++ applications which will directly interact with PDAL.

%files -n %{devname}
%{_bindir}/pdal-config
%{_includedir}/pdal/
%exclude %{_libdir}/libpdal_plugin_kernel_fauxplugin.so
%exclude %{_libdir}/libpdal_plugin_reader_pgpointcloud.so
%exclude %{_libdir}/libpdal_plugin_writer_pgpointcloud.so
#{_libdir}/libpdal_base.so
#{_libdir}/libpdal_util.so
%{_libdir}/libpdalcpp.so
%{_libdir}/cmake/PDAL/
%{_libdir}/pkgconfig/*.pc

#--------------------------------------------------------------------

%if %{with doc}
%package doc
Summary:	Documentation for PDAL
BuildArch:	noarch

%description doc
This package contains documentation for PDAL.

%files doc
%license LICENSE.txt
%doc doc/build/html
%endif

#--------------------------------------------------------------------

%prep
%autosetup -p1 -n PDAL-%{version}-src

# Remove some bundled libraries
rm -rf vendor/{eigen,gtest,pdalboost}

%build
%cmake	\
	-D PDAL_LIB_INSTALL_DIR:PATH=%{_lib} \
	-D CMAKE_INSTALL_LIBDIR:PATH=%{_lib} \
	-D CMAKE_VERBOSE_MAKEFILE=ON \
	-D GEOTIFF_INCLUDE_DIR=%{_includedir}/libgeotiff \
	-D BUILD_PGPOINTCLOUD_TESTS:BOOL=OFF \
	-D WITH_COMPLETION=ON \
	-D WITH_LAZPERF=ON \
	-D WITH_TESTS=ON \
	-D PDAL_HAVE_LIBGEOTIFF=ON \
	-D PDAL_HAVE_LIBXML2=ON \
	-D POSTGRESQL_INCLUDE_DIR=%{_includedir}/pgsql \
	-D POSTGRESQL_LIBRARIES=%{_libdir}/libpq.so \
	-GNinja
%ninja_build

# docs
%if %{with doc}
pushd doc
sphinx-build -b html . build/html
popd
%endif

%install
%ninja_install -C build

%check
pushd build
#ctest || :
popd

