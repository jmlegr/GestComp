Ext.define('GestComp.Prof.controller.Test', {
    extend: 'Ext.app.Controller',
    //views:'eleves.Liste',
    models:['Eleve'],
    stores:['Eleves'],
	//require: ['GestComp.profs.view.eleve.Liste'],
    init: function() {
    	/*
        this.control({
            'eleveliste': {
                itemdblclick: this.editEleve
            }
        });
        */
    	this.control({
    	 'panel[class="x-panel-header"]': {
    	 	resize: this.clic,
    	 	render:this.rendu,
    	 }
    	})
        console.log('Initialized Users! This happens before the Application launch function is called');
        var E=this.getElevesStore();
        console.log('store',E)
    },
	clic:function() {console.log('clicked')},
	rendu:function() {console.log('rendu')},
    editEleve: function(grid,record) {
       console.log('Double clicked on ' + record.get('name'));
    }
});