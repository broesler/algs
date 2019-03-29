/*=============================================================================
 *    File: sort.c
 * Created: 07/17/14
 *  Author: Bernie Roesler
 *
 * Synopsis: sort [-nru] file
 *
 * Description: Much like the shell sort command, but limited to numbers stored
 *  in a file given as an input argument. Default sort is alphabetic. Uses the
 *  quicksort algorithm, implemented recursively.
 *
 * Input: Filename. The following options are available:
 *      -n      compare according to string numerical value
 *      -r      reverse the result of comparisons
 *      -u      output only the first of an equal run (no repeating lines)
 *
 * Output: List of lines in file according to options given above.
 *===========================================================================*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* #include <assert.h> */
/* #include <time.h> */

/* User-defined header file for malloc checks */
#include "header.h"

#define MAXCHAR 81  /* Maximum line length (incl. `\0') */
#define MAXN  1000  /* Maximum number of sortable elements (per malloc) */

/* Function Prototypes */

/* The standard quicksort prototype: */
/* void qsort(void *base, size_t nmemb, size_t size, */
/*            int (*compar)(const void *, const void *)); */

/* int functions */
void printIntArray(int *ap, int len);
void quicksort(int *a, int lo, int hi);
int partition(int *a, int lo, int hi);
void swap(int *a, int *b);

/* string functions */
void quicksortStr(char **a, int lo, int hi);
int partitionStr(char **a, int lo, int hi);
void printStrArray(char **ap, int len);
void swapStr(char **a, char **b);

/*-----------------------------------------------------------------------------
 *    main function
 *---------------------------------------------------------------------------*/
int main(int argc, char *argv[]) 
{

    int i,j;
    int unique = 0,   /* Options flags */
        reverse = 0,
        numsort = 0;     
    char *filename;
    FILE *ifp;        /* (i)n (f)ile (p)ointer */

    /*---------------------------------------------------------------------------
     *    Parse Arguments
     *-------------------------------------------------------------------------*/
    if (argc <= 1) {
        printf("Usage: ./sortc [-nru] [filename]\n");
        exit(-1);
    }

    /* run through the input commands looking for switches */
    while ((argc > 1) && (argv[1][0] == '-')) {

        /* check each character in the option for a valid switch */
        i = 1;  /* argv[1][0] is the '-' character */
        while ( argv[1][i] != '\0' ) {

            switch (argv[1][i]) {
                case 'r':
                    reverse = 1;
                    break;
                case 'u':
                    unique = 1;
                    break;
                case 'n':
                    numsort = 1;
                    break;

                default:
                    printf("Usage: bad option %c\n", argv[1][i]);
                    exit(-1);
            }

            i++; /* move to next character in option */
        } /* end while checking argv chars */

        /* decrement the number of arguments left */
        /* increment the argv pointer to the next argument */
        argc--;
        argv++;
    } /* end while checking argv */

    /* After all switches are read, read filename */
    filename = *(argv+1);
    /* printf("Filename: %s\n", filename); */

    /*---------------------------------------------------------------------------
     *    Perform Sort and Output
     *-------------------------------------------------------------------------*/
    ifp = fopen(filename, "r");   /* open file */
    /* assert(ifp != NULL);          #<{(| ensure file is open and readable |)}># */
    if (ifp == NULL) {
        fprintf(stderr, "sortc: %s: No such file or directory.\n", filename);
        return 1;
    }

    int N = MAXN, 
        len = 0; /* keep track of array size */

    /*---------------------------------------------------------------------------
     *    If numsort == 1, read file as integers, else, read as strings
     *-------------------------------------------------------------------------*/
    if (numsort == 1) {

        /* Read file in as integers */
        int *numarray = (int *)calloc(N, sizeof(int));    /* initialize integer array */
        MALLOC_CHECK(numarray);

        i = 0;
        while (fscanf(ifp, "%d\n", &numarray[i]) != EOF) {

            /* if buffer overrun, increase array size */
            if (i == MAXN) {
#ifdef LOGSTATUS
                LOG("Realloc'ing memory!");
#endif
                N = (int)(N * 1.5);
                numarray = realloc(numarray, N*sizeof(int));
                MALLOC_CHECK(numarray);
            }
            i++;
        }

        len = i-1;    /* final index of things to sort */

        /* Sort contents of array (as integers) */
        quicksort(numarray, 0, len);

        /* Print out results */
        if (reverse == 0) {
            if (unique == 0) {
                printIntArray(numarray, len+1);         /* print sorted array */
            } else {                                  /* unique == 1 */
                printf("%d\n", numarray[0]);            /* print 1st element */
                for (i=1; i < len+1; i++) {                
                    if (numarray[i] != numarray[i-1])     /* check for repeats */
                        printf("%d\n", numarray[i]);
                }
            }
        } else {                                    /* print array in reverse order */
            if (unique == 0) {
                for( i=len; i >= 0; i--)
                    printf("%d\n", numarray[i]);
            } else {
                printf("%d\n", numarray[len]);
                for( i=len; i > 0; i--) {
                    if (numarray[i-1] != numarray[i])
                        printf("%d\n", numarray[i-1]);
                }
            }
        }

        free(numarray); /* free pointer */

    } else {             
        /*-------------------------------------------------------------------------
         *    (if numsort == 0) Read in each line as a string 
         *-----------------------------------------------------------------------*/

        /* Read file in as strings */
        char buffer[MAXCHAR];
        char **numarray = malloc( MAXN*sizeof(char *) );  /* allocates memory for pointers to MAXN characters */
        MALLOC_CHECK(numarray);

        i = 0;
        while( fgets(buffer, sizeof(buffer), ifp) != NULL ) {

            /* memory check */
            if (i == N-1) { /* on last pointer of array! */
#ifdef LOGSTATUS
                LOG("Realloc'ing memory!");
#endif
                N = (int)(N * 1.5);
                numarray = realloc( numarray, N*sizeof(char *) ); /* reallocate 1.5x pointers in array */
                MALLOC_CHECK(numarray);
            }

            j = strlen(buffer)-1;

            if ( buffer[j] == '\n' ) {   /* remove newline from buffer */
                 buffer[j]  = '\0';      /* null terminate string */
            }
            
            /* Copy buffer into numarray */
            numarray[i] = malloc(MAXCHAR*sizeof(char));
            MALLOC_CHECK(numarray[i]);
            BZERO(numarray[i], MAXCHAR*sizeof(char));
            MYASSERT(strcpy(numarray[i], buffer));

            i++;
        }
        len = i-1;    /* last index == (number of things to sort) - 1 */

        /* Sort contents of array (as strings) */
        quicksortStr(numarray,0,len);

        /* Print out results */
        if (reverse == 0) {
            if (unique == 0) {
                printStrArray(numarray, len+1);    /* print sorted array */
            } else {                                        /* unique == 1 */
                printf("%s\n", numarray[0]);                  /* print first element */
                for(i = 1; i < len+1; i++) {                
                    if ( strcmp(numarray[i],numarray[i-1]) != 0)           /* check for repeats */
                        printf("%s\n", numarray[i]);
                }
            }
        } else {  /* print array in reverse order */
            if (unique == 0) {                /* just print array */
                for(i = len; i >= 0; i--)
                    printf("%s\n", numarray[i]);
            } else {                          /* print only unique values */
                printf("%s\n", numarray[len]);  /* print last number first */
                for(i = len; i > 0; i--) {
                    if ( strcmp(numarray[i-1],numarray[i]) != 0)
                        printf("%s\n", numarray[i-1]);
                }
            }
        }

        /* Free allocated memory */
        for (i = 0; i <= len; i++) {
            free(numarray[i]); 
            numarray[i] = NULL;
        }
        free(numarray);

    } /* if numsort == 1 */

    fclose(ifp);

    return 0;
} /* main */



/*=============================================================================
 *    FUNCTIONS
 *===========================================================================*/


/*------------------------------------------------------------------------------
 *      Integer functions
 *----------------------------------------------------------------------------*/
void printIntArray(int *ap, int len) 
{
    for(int i = 0; i < len; i++) {
        printf("%d\n", ap[i]);
    }
}

void quicksort(int *a, int lo, int hi) 
{
    if (lo < hi) {
        int p = partition(a, lo, hi);
        quicksort(a, lo, p-1);
        quicksort(a, p+1, hi);
    }
}

int partition(int *a, int lo, int hi) 
{
    int *paddr = &a[lo]; /* pivot address (needs to update with swaps!) */
    int piv = a[lo],    /* pivot value (doesn't change with swaps) */
        i = lo + 1;

    while (i <= hi) {
        /* compare to pivot */
        if (a[i] < piv) {
            /* move element left of the pivot */
            swap(&a[i], &a[lo]);

            /* keep paddr on the actual pivot element */
            if (paddr == &a[lo]) {
                paddr = &a[i]; 
            }

            lo++;   /* move up border of high/low elements */
        }
        i++; /* move on to next element */
    }

    /* move pivot into correct location in array */
    if (paddr != &a[lo]) {
        swap(paddr, &a[lo]); 
    }

    /* return index of pivot element */
    return lo;
}

/* swap two integer array elements */
void swap(int *a, int *b) 
{
    int temp = *a;  /* swap actual values */
    *a = *b;
    *b = temp;
}

/*------------------------------------------------------------------------------
 *      String functions
 *----------------------------------------------------------------------------*/
void printStrArray(char **ap, int len) 
{
    for(int i = 0; i < len; i++) {
        printf("%s\n", ap[i]);
    }
}

void quicksortStr(char **a, int lo, int hi) 
{
    if (lo < hi) {
        int p = partitionStr(a, lo, hi);
        quicksortStr(a, lo, p-1);
        quicksortStr(a, p+1, hi);
    }
}

int partitionStr(char **a, int lo, int hi) 
{
    char **paddr = &a[lo]; /* pivot address (needs to update with swaps!) */
    char *piv = a[lo]; /* pivot value (does not change with swaps) */
    int i = lo + 1;

    while (i <= hi) {
        if (strcmp(a[i],piv) < 0) {
            /* move element to left of pivot */
            swapStr(&a[i], &a[lo]);

            /* keep paddr on the actual pivot element */
            if (paddr == &a[lo]) {
                paddr = &a[i]; 
            }

            lo++;
        }
        i++;
    }

    /* move pivot into correct location in array */
    if (paddr != &a[lo]) { 
        swapStr(paddr, &a[lo]);
    }

    /* return index of pivot element */
    return lo;
}

/* swap two char* array elements (i.e. strings) */
void swapStr(char **a, char **b)
{
    char *temp = *a;
    *a = *b;
    *b = temp;
}

/*=============================================================================
 *===========================================================================*/
