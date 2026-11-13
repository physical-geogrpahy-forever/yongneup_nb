      subroutine daily(mly,dly)
      implicit none
      real mly(12),dly(365),midday(12),vinc
      integer im,id
      data (midday(im),im=1,12)/16., 44., 75.,105.,136.,166.,
     >                         197.,228.,258.,289.,319.,350./

      vinc=(mly(1)-mly(12))/31.0
      dly(350)=mly(12)
      do 100 id=351,365
         dly(id)=dly(id-1)+vinc
100      continue
      dly(1)=dly(365)+vinc
      do 101 id=2,15
         dly(id)=dly(id-1)+vinc
101      continue
      do 103 im=1,11
         vinc=(mly(im+1)-mly(im))/(midday(im+1)-midday(im))
         dly(int(midday(im)))=mly(im)
         do 104 id=int(midday(im))+1,int(midday(im+1))-1
            dly(id)=dly(id-1)+vinc
104         continue
103      continue
      return
      end   
      subroutine snow(dtemp,dprec,dmelt,dprecin,maxdepth)
      implicit none
      integer day,it
      real dtemp(1:365),dprec(1:365),dprecin(1:365)
      real tsnow,km,snowpack,snowmelt,newsnow,drain
      real dmelt(365),sum1,sum2,maxdepth
      parameter(tsnow=-1.,km=0.7)
      
      snowpack = 0.0
      maxdepth = 0.0

      do it =1,2
       sum1=0.
       sum2=0.

       do day=1,365
   
        drain = dprecin(day) / (365./12.)

c       Calculate snow melt and new snow for today
        if(dtemp(day).lt.tsnow)then
         newsnow  = drain
         snowmelt = 0.
        else
         newsnow  = 0.
         snowmelt = km*(dtemp(day)-tsnow)
        endif

c       Reduce snowmelt if greater than total snow remaining
        if (snowmelt.gt.snowpack) snowmelt = snowpack
    
c       Update snowpack store
        snowpack = snowpack + newsnow - snowmelt
        if (snowpack.gt.maxdepth) maxdepth=snowpack

c       Calculate effective water supply (as daily values in mm/day)
        dprec(day) = drain - newsnow 
        dmelt(day) = snowmelt

        sum1=sum1+dprec(day)+dmelt(day)
        sum2=sum2+drain

       end do
      end do

      return
      end