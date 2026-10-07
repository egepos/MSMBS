## Assignment 5

##### Task 1:

![img.png](img.png) - initial state ![img_1.png](img_1.png) - 30 minutes run ![img_2.png](img_2.png) - 60 minutes run![img_4.png](img_4.png) - 90 minutes run ![img_3.png](img_3.png) - 120 minutes run

The infected tissue spreads starting from cells that were the closest to the interveining pathogen. Pathogen itself grows slower than the infection overall. Deformation primarily happens due to the pressure of the infection on the surrounding healthy tissue. As pathogen grows, it exerts pressure on the surrounding healthy tissue, causing it to deform and potentially leading to tissue damage. The relaxation of the tissue also contributes to the change in the initial shape.

#### Task 2:
```
double patho_chem_level = c->Chemical(0) / (0.5);
    if (patho_chem_level > 1.2) {
        patho_chem_level = 1.2;
    }
    double stiffness_inf = 3;
    if(patho_chem_level>0.1 && c->CellType()!=2){
        c->SetCellVeto(false);
        stiffness_inf = 3 - (patho_chem_level);
    c->LoopWallElements([stiffness_inf](auto wallElementInfo){
        wallElementInfo->getWallElement()->setStiffness(stiffness_inf);
    });
    }
    else{
        c->LoopWallElements([stiffness_inf](auto wallElementInfo){
        wallElementInfo->getWallElement()->setStiffness(stiffness_inf);
        });
        c->SetCellVeto(true);
    }
   ```
The function above describes the mechanism of cells' wall. The mechanism is dependent on the pathogen chemistry level. Once it goes over 0.1 (and cell type does not equal 2). Stiffness level of a cell drops from 3 based on the chemistry level of the pathogen. Pathogen itself is not affected by the function. In case pathogen chemistry level drops, the stiffness level can return to normal.

#### Task 3:

```
void Infection::CelltoCellTransport(Wall *w, double *dchem_c1, double *dchem_c2) {
	// add biochemical transport rules here
    double sum =  w->C1()->Area() + w->C2()->Area();
    double corr1 = w->C2()->Area() / sum;
    double corr2 = w->C1()->Area() / sum;

    double length = 1.0;
    double stiffness = 1.0;
    getLengthAndStiffness(w,&length,&stiffness);
    double diffusionCoef;
    if(stiffness>0.001){
        diffusionCoef = 0.00001/stiffness;
    }
    else{diffusionCoef=0.00001;}

    double phi = length * diffusionCoef * ( w->C2()->Chemical(0) - w->C1()->Chemical(0) );

    dchem_c1[0] += corr1 * phi;
    dchem_c2[0] -= corr2 * phi;
 ```
    
In the above code, diffusion coefficient is defined once the stiffness of a cell is at least larger than 0.001. It is then a equal to the division 0.00001 by the stiffness of a cell. If the stiffness is less than 0.001, the diffusion coefficient is set to 0.00001.