/*
 * Controller: navigation.Evaluation
 * controle les changements d'affichage quand une évaluation est sélectionnée dans le panel navigation
 */
 
Ext.define('GestComp.Prof.controller.navigation.Evaluation', {
    extend: 'Ext.app.Controller',
    views: ['navigation.Evaluation','evaluation.Affichage'],

    refs:[{ 	
    	ref:'affichage',
    	selector:'evaluation_affichage'
    },{
    	ref:'resultats',
    	selector:'evaluation_affichage #tab-resultats'
    },{
    	ref:'autres',
    	selector:'evaluation_affichage #tab-autres'
    }],
    
    stores:['Evaluations'],
    init: function() {
    	//activation des tabs
    	this.control({
    		'navigation_evaluation': {   		
    			'itemclick':{
	    			fn:this.activeTabs,
    				single:true    			
    			}
    		}
    	});
    	// mise à jour de la barre de titre, des infos élèves
    	this.control({
    		'navigation_evaluation': {   		
    			'itemclick':{
    				fn:this.selectClickEvaluation,
    				buffer:1000 
    			}    			
    		}
    	});		
    	
    },
    selectClickEvaluation:function(view,record,item,index){    	
    	this.getAffichage().updateTitle(record);    	
    	this.getAutres().tpl.overwrite(this.getAutres().body,record.data)
    	this.getResultats().reload(record.get('id'))
 		
 	},
 	
 	activeTabs:function() {
 		//activation des onglets lors du premier select
 		this.getAffichage().items.eachKey(function(key,item){item.setDisabled(false)})
 	}
});
