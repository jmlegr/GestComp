/*
 * Controller: Navigation
 * Fait le lien entre la manel naviagtion et le panel d'affichage principal
 */
 
Ext.define('GestComp.Prof.controller.Navigation', {
    extend: 'Ext.app.Controller',
    views: ['Navigation','affichage.Principal'],
    refs:[{
    	ref:'affichage_principal',
    	selector:'affichage_principal',
    }],
    
    init: function() {
    	var me=this
    	this.control({
    		
    	'navigation > panel': {
    		'expand':this.changeAffichage    		
    		}
    	})
  
    },
    changeAffichage:function(item){    	
    	this.getAffichage_principal().getLayout().setActiveItem(item.id)    	
    }
	
});