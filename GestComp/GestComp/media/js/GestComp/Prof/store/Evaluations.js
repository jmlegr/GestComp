Ext.define('GestComp.Prof.store.Evaluations',{
	extend:'Ext.data.Store',
	autoLoad: true,
	requires:['GestComp.Prof.model.Evaluation'],
	model:'GestComp.Prof.model.Evaluation',
	sorters:[{property:'date_modification',direction:'DESC'},],
	groupField:'perso',
	
});
        		   