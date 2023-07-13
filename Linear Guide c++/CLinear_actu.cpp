#include "CLinear_actu.h"


char mot_file[] = "C:\Users\송환진\Downloads\Interfacing File 1\Linear Guide c++\ajin20190628.mott";        //*.mot file Path
int vel = 700;
int accel = 200;

CLinear_actu::CLinear_actu()
{
	DWORD Code = AxlOpen(7);
	if (Code == AXT_RT_SUCCESS)
	{
		printf("Library Reset. \n");
		//Check for Motion Module
		DWORD uStatus;
		Code = AxmInfoIsMotionModule(&uStatus);
		if (Code == AXT_RT_SUCCESS)
		{
			printf("Library Reset.\n");
			if (uStatus == STATUS_EXIST)
			{
				printf("Library Reset. \n");

				AxmMotLoadParaAll(mot_file);

				AxmStatusSetActPos(0, 0.0);
				AxmStatusSetCmdPos(0, 0.0);

				AxmSignalServoOn(0, ENABLE);

				AxmMotSetAbsRelMode(0, 1); //0->abs, 1->Rel
				AxmMotSetProfileMode(0, 3);	//0->symetric trapezode, 1->unsymetric trapezode, 2->reserved, 3->symetric S Curve, 4->unsymetric S Cuve
			}
		}
	}
}


CLinear_actu::~CLinear_actu()
{
	AxmSignalServoOn(0, 0);
	AxlClose();
}


void CLinear_actu::move_actu(int pos)
{
	AxmMovePos(0, pos, vel, accel, accel);
	DWORD uStatus;
	AxmStatusReadInMotion(0, &uStatus);
	while (uStatus)
	{
		AxmStatusReadInMotion(0, &uStatus);
	}
}
