/*
 * Controller: navigation.Eleve
 * controle les changements d'affichage quand un élève est sélectionné dans le panel navigation
 */
 
Ext.define('GestComp.Prof.controller.navigation.Eleve', {
    extend: 'Ext.app.Controller',
    views: ['navigation.Eleve'],
    refs:[{    	
    	ref:'infosEleve',
    	selector:'infoseleve'
    },{
    	ref:'affichage',
    	selector:'eleve_affichage'
    }],
    
    stores:['Eleves'],
    init: function() {
    	//activation des tabs
    	this.control({
    		'navigation_eleve': {   		
    			'itemclick':{
	    			fn:this.activeTabs,
    				single:true    			
    			}
    		}
    	});
    	// mise à jour de la barre de titre, des infos élèves
    	this.control({
    		'navigation_eleve': {   		
    			'itemclick':{
    				fn:this.selectClickEleve,
    				buffer:1000 //a changer, juste pour memoire pour les chargements de données
    			}    			
    		}
    	});		
    	this.control({
    		'viewport': {
    			beforehide:this.test
    		}
    	})
    },
    test:function(){console.log('click'); alert('destroy')},
    selectClickEleve:function(view,record,item,index){    	
    	this.getAffichage().updateTitle(record);
 		this.getInfosEleve().updateDetail(record);
 	},
 	
 	activeTabs:function() {
 		//activation des onglets lors du premier select
 		this.getAffichage().items.eachKey(function(key,item){item.setDisabled(false)})
 	}
});