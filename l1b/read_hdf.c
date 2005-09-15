#include "hdf.h"

#define  N_FIELDS        9
#define  VDATA_NAME      "SMR"
#define  FIELDNAME_LIST  "Version,Level,MJD,Orbit,Source,Type,Latitude,Longitude,SunZD"
#define  BUFFER_SIZE     ( 3*sizeof(short)+2*sizeof(double)+sizeof(char[32])+3*sizeof(float)) 

/* compile with gcc read_hdf.c -lmfhdf -ldf -ljpeg -lz -o read_hdf */

int main (int argc,char *argv[])
{
    /************************* Variable declaration **************************/

    intn    status_n;      /* returned status for functions returning an intn  */
    int32   status_32,     /* returned status for functions returning an int32 */
            file_id,
            vdata_id,
            interlace_mode,
            vdata_size,
            n_records,
            num_of_records,        /* number of records actually read */
            vdata_ref,             /* reference number of the vdata to be read */
            buffer_size;           /* number of bytes the vdata can hold       */

    char field_name_list[512],vdata_name[20]; /*holds string names*/

    uint8 databuf[BUFFER_SIZE];  /* buffer to hold read data, still packed   */
    VOIDP fldbufptrs[N_FIELDS];/*pointers to be pointing to the field buffers*/
    int   i;

    /* variables mapped to data */
    short   Version,
            Level,
            Type;
    double  MJD,
            Orbit;
    char    Source[32];
    float   Latitude,
            Longitude,
            SunZD;

    /********************** End of variable declaration **********************/


    /* initiate hdf file */
    file_id = Hopen (argv[1], DFACC_READ, 0);
    status_n = Vstart (file_id);
    vdata_ref = VSfind (file_id, VDATA_NAME);
    vdata_id = VSattach (file_id, vdata_ref, "r");
    status_n= VSsetfields(vdata_id, FIELDNAME_LIST);

    /* read record numbers */
    status_n = VSinquire(vdata_id, &n_records, &interlace_mode, field_name_list, &vdata_size, vdata_name);

    fldbufptrs[0] = &Version;
    fldbufptrs[1] = &Level;
    fldbufptrs[2] = &MJD;
    fldbufptrs[3] = &Orbit;
    fldbufptrs[4] = &Source;
    fldbufptrs[5] = &Type;
    fldbufptrs[6] = &Latitude;
    fldbufptrs[7] = &Longitude;
    fldbufptrs[8] = &SunZD;

    for (i=0;i<n_records;i++){
        num_of_records = VSread (vdata_id, (uint8 *)databuf, 1, interlace_mode);

        status_n = VSfpack (vdata_id, _HDF_VSUNPACK, FIELDNAME_LIST, (VOIDP)databuf,BUFFER_SIZE, num_of_records, NULL, (VOIDP)fldbufptrs);

        printf ("%d;%d;%.15f;%.15f;%s;%d;%.15f;%.15f;%.15f;\n", Version,Level,MJD,Orbit,Source,Type,Latitude,Longitude,SunZD);
    }

    status_32 = VSdetach(vdata_id);

    status_n = Vend (file_id);

    status_32 = Hclose (file_id);
}
