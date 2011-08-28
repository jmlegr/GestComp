Ext.define('GestComp.Prof.view.eleve.Infos',{
 	extend:'Ext.Panel',
 	alias:'widget.infoseleve',
     border:false
    ,initComponent:function() {
		this.defaults={autoScroll:true};        	
		this.detailTpl= new Ext.XTemplate('' +
			'<div >',
			'<table border="0" cellpadding="0" cellspacing="0" width="100%" height="100%">',
				'<tr><td align="center" valign="middle">',
				'<table border="0" cellpadding="2" cellspacing="2" align="center" width="75%" class="cssDetailsTable">',
					'<tr>',
						'<td class="cssDetailsLabel" width="30%">Nom</td>',
						'<td class="cssDetailsData">{[values.nom.toUpperCase()]}</td>',
					'</tr>',
					'<tr>',
						'<td class="cssDetailsLabel" width="30%">Prénom</td>',
						'<td class="cssDetailsData"> {[Ext.String.capitalize(values.prenom)]}</td>',
					'</tr>',
					'<tr>',
						'<td class="cssDetailsLabel" width="30%">Classe</td>',
						'<td class="cssDetailsData">{classe}</td>',
					'</tr>',
					'<tr>',
						'<td class="cssDetailsLabel" width="30%">Groupes</td>',
						'<td class="cssDetailsDataMini">{groupes}</td>',						
					'</tr>',
				'</table>',
				'</td></tr>',
			'</table>',
			'</div>');
		this.html='<div class="cssDefault"><i>Choisissez un élève dans la grille de gauche</i></div>';
		this.updateDetail=function(record) {
    			this.detailTpl.overwrite(this.body,record.data)
    	};	
		this.callParent();
    }
}); // eo extend