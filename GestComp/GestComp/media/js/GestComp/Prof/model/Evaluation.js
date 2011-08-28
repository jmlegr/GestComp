Ext.define('GestComp.Prof.model.Evaluation',{
	extend:'Ext.data.Model',
	fields:['id','nom',
		{name:'date_modification',type: 'date', dateFormat: 'c'},
		{name:'date_evaluation',type: 'date', dateFormat: 'c'},
		{name:'perso',type:'boolean'},
		{name:'user'}
		],
	proxy:{
		type:'ajax',
		url:'/evaluations/liste_evaluations',
		extraParams: {action:'tout'},
		reader: {
            type: 'json',
            root: 'data'
        }
	}
});      	
