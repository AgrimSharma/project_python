/// <reference path='../../_all.ts' />
// checking collision when moving cells or creating new cells

module scrumdo {
    export class BoardCollisionHelper {

        constructor (
            public selectedCells: Array<any>,
            public scope) {

        }

    public tooltip() {
        // create tooltip for board editor
        return d3.select("body").append("div")    
        .attr("class", "tooltip")                
        .style("opacity", 0)
        .style("left", (window.innerWidth/2 - 100) + "px")       
        .style("top", 90 + "px");
    }

    public validateCellCoordinates = () => {
        var isNotValid;
        this.selectedCells.forEach( (cell) => {
            if(cell.gridsx() < 0 || cell.gridsy() < 0) {
                isNotValid = true;
            }
        });
        return isNotValid;
    }

    public checkCollision = (selected) => {
        // check overlapping cells
        var isCollide;
        this.scope.cells.forEach( (cell) => {
            if(this.selectedCells.indexOf(cell) > -1) return;

            var otherCell = document.getElementById('cell_' + cell.id);
            var selectedCell;
            if(selected.id) {
                selectedCell = document.getElementById('cell_' + selected.id);
                if(selectedCell == null){
                    selectedCell = document.getElementById('header_' + selected.id);
                }
            } else {
                selectedCell = document.getElementsByClassName('current-drawing-header')[0];
            }
              

            var rect2 = otherCell.getBoundingClientRect();
            var rect1 = selectedCell.getBoundingClientRect();
            var collide = (
                rect1.top >= rect2.bottom ||
                rect1.right <= rect2.left ||
                rect1.bottom <= rect2.top ||
                rect1.left >= rect2.right 
                );
            
            if(!collide) {
                isCollide =true;
            }
        });
        return isCollide;
        }
    }
  
}