LDLIBS= -lnetcdf -lhdf5_hl -lhdf5 -lz -lm 
#LDFLAGS= -L/lib -L/home/odinop/hermod_production_2.7/parts/hdf5/lib -Wl,-rpath=/home/odinop/hermod_production_2.7/parts/netcdf/lib,-rpath=/home/odinop/hermod_production_2.7/parts/hdf5/lib
#INCLUDES= -I/home/odinop/hermod_production_2.7/parts/netcdf/include -I/home/odinop/hermod_production_2.7/parts/hdf5/include
#to build with outputs -> comment SILENT
SILENT= -DODINECMWF_SILENT
CPPFLAGS= $(INCLUDES) $(SILENT)
CFLAGS= -g -fpic -Wall -z muldefs
 
#SHARED= --shared -Wl,-soname,odinp_grib2.so.1 
SHARED= --shared 

all: shared exec

shared: odinecmwf_grib2.so

exec: odinecmwf_grib2

#Rule to link as a shared library
%.so: %.o
	$(CC) $(LDFLAGS) $^ $(LDLIBS) $(SHARED) -o $@

distclean: clean

clean:
	$(RM) odinecmwf_grib2.so odinecmwf_grib2.o odinecmwf_grib2 

