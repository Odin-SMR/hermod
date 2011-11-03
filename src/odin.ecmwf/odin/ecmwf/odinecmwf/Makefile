LIBS= -lnetcdf -lhdf5_hl -lhdf5 -lz -lm 
LIB_DIRS = -L/usr/local/lib
INCLUDES= -I/usr/local/include
#to build with outputs -> make SILENT=""
SILENT= -DODINECMWF_SILENT
CPPFLAGS= $(INCLUDES) $(SILENT)
CFLAGS= -g -fpic -Wall -z muldefs
 
#SHARED= --shared -Wl,-soname,odinp_grib2.so.1 
SHARED= --shared 
LDFLAGS=  $(LIB_DIRS) $(LIBS) 

all: shared exec

shared: odinecmwf_grib2.so

exec: odinecmwf_grib2

#Rule to link as a shared library
%.so: %.o
	$(CC) -o $@  $< $(SHARED) $(LDFLAGS)

distclean: clean

clean:
	$(RM) -f odinecmwf_grib2.so odinecmwf_grib2.o odinecmwf_grib2 

