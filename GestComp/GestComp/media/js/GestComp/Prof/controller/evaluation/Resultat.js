var po=0
Ext.define('GestComp.Prof.controller.evaluation.Resultat', {
    extend: 'Ext.app.Controller',
    views: ['navigation.Evaluation','evaluation.Affichage'],
    
    refs:[{ 	
    	ref:'affichage',
    	selector:'evaluation_affichage'
    },{
    	ref:'grille_resultats',
    	//selector:'evaluation_affichage #tab-resultats'
    	selector:'evaluation_affichage #grille_resultats'
    },{
    	ref:'general',
    	selector:'evaluation_affichage #tab-autres > #infos_eval_general'
    },{
    	ref:'detail',
    	selector:'evaluation_affichage #tab-autres > #infos_eval_detail'
    }],
    
    stores:['Evaluations'],
    init: function() {
    	console.log('init res')
    	this.control({
    		//'evaluation_resultats': {
    		'dynamic_grid': {
    			'edit':function(ed,e,opt)    				
    				{
    				donnees='donnees'+e.field.substring(e.field.indexOf('_'))
    				console.log(po++,'startEdiot',donnees,e.record.isModified(donnees),e.record.modified,e.record.getChanges())
    				console.log('====',e)
    				/*
    				 
    				 for (var f in e.record.modified) {
    					var same=true
    					for (var key in e.record.modified[f]) {
    						if (e.record.modified[f][key]!==e.record.getChanges()[f][key]) {    							
    							console.log('key',key,e.record.modified[f][key],e.record.getChanges()[f][key])
    							same=false;
    							break;
    						}
    					}
    					console.log('field',f,same)
    				}
    				*/
    				/*if (same) {
    					console.info('commi')
    					e.record.commit()
    				}*/
    				if (e.record.isModified(donnees)) {
    					console.log('Donnees modifées on sauvegarde')
    				} else {
    					console.log('Dionneees non modifess on annule')
    					//e.record.commit(true)
    					//e.record.reject(true)
    					e.record.cancelEdit()
    				}
    				//ed.cancelEdit()
    				},
    			'select':function(selModel,record,row,column,opts) {console.log('select',record,row,column)}
    			
    		},
    		'evaluation_resultats #btn_sauvegarder': {
    			'click':function() {console.log('click')
    				 recs=this.getGrille_resultats().getStore().queryBy(
    					function(e,i) {return e.dirty})
    				console.log(recs,this.getGrille_resultats().getStore().getUpdatedRecords())
    				//recs.each(function(r){console.log(r.getChanges())})
    				//recs.each(function(r){console.log(r); r.cancelEdit()})
    				 }
    		}
    	})
    	
    },
    
});