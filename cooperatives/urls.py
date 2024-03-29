from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static

from .views import (
    RemplaceSave,
    changeSection,
    consult_histo,
    contactProd,
    coop_dashboard,
    add_section,
    add_sous_section,
    createDetailmonitoring,
    createDetailplanting,
    createEspecemonitoring,
    createParcelle,
    createPlanting,
    createProducteurs,
    deleteEspece,
    deletes,
    edit_formatoin,
    edit_monitoring,
    edit_monitoring_view,
    edit_parcelle,
    edit_product,
    edit_productor,
    edit_section,
    edit_sous_section,
    endremplaceSave,
    espece_monitoring_view,
    esrempla_monitoring_view,
    export_formation_to_pdf,
    export_parcelles_to_pdf,
    formationSave,
    getListParcForcoop,
    getMonitoringForcoop,
    getProducteursForcoop,
    importAnnuleProd,
    importValidProd,
    monitoring_form_view,
    monitoringCreate,
    monitoringSave,
    obsMonitoringFunc,
    parcTableFunction,
    parcelle_update,
    parcelleSave,
    participant_delete,
    plantTableFunction,
    plantingSave,
    prodTableFunction,
    producteurSave,
    producteurs,
    production,
    # cooperative,
    prod_update,
    prod_delete,
    parcelles,
    parcelle_delete,
    # planting,
    # planting_update,
    formation,
    detail_formation,
    AddPlantingView,
    export_planting_xls,
    # use Ajax and jquery request
    my_section,
    export_producteur_csv,
    # PlantingDelete,
    export_prods_to_pdf,
    export_prod_xls,
    export_parcelle_xls,
    export_plant_xls, Editformation,
    production_delete,
    production_update,
    productionSave,
    rempend_monitoring_view,
    remplacement_monitoring_view,
    saveParticipant,
    saveProdFile,
    tranning,
    update_formation, delete_section, export_section_xls,
    update_section,
    update_sous_section,
    export_sous_section_xls, export_formation_xls, delete_sous_section, ParcellesMapView, parcelle_list, ReceptionView,
    folium_map, PlantingList, detail_planting, coopdetailPlantings, CoopPlantings, getParcelleCoop, map_by_cooperative,
    updateMonitoring,
    updateProducteur,
    view_historique,
    # delete_sous_section, export_sous_section_xls, export_formation_xls, my_parcelles, ParcellesView,
    # load_section
)

app_name='cooperatives'

urlpatterns = [
    # Patient
    # path('cooperative/<int:id>', cooperative, name='cooperative'),
    path('producteur/<str:code>/modifier', prod_update, name='modifier'),
    path('producteur/<str:code>/supprimer', prod_delete, name='del_producteur'),
    # path('parcelle/<int:id>', parcelle_delete, name='del_parcelle'),
    path('parcelle/<str:code>/modifier', edit_parcelle, name='edit_parcelle'),
    path('parcelle/<str:code>/supprimer', parcelle_delete, name='parcelle_delete'),
    path('section/<int:id>/delete/supprimer', delete_section, name='delete_section'),

    path('sous_section/<int:id>/supprimer', delete_sous_section, name='delete_sous_section'),
    path('dashboard/', coop_dashboard, name='dashboard'),
    path('sections/', add_section, name='section'),
    path('sous_sections/', add_sous_section, name='sous_sections'),
    path('formation/', formation, name='formations'),
    path('Editformation/<int:id>', Editformation, name='Editformation'),
    path('formation/<int:id>', detail_formation, name='formation'),
    path('producteurs/', producteurs, name='producteurs'),
    path('parcelles/', parcelles, name='parcelles'),
    #path('my_parcelles/', my_parcelles, name='my_parcelles'),
    # path('plantings/', planting, name='planting'),
    path('planting_coop/', CoopPlantings, name='CoopPlantings'),
    path('coopdetailPlantings/', coopdetailPlantings, name='coopdetailPlantings'),
    path('plantings/<str:code>/', detail_planting, name='suivi_planting'),
    path('add_planting/', AddPlantingView.as_view(), name='add_planting'),
# detail_planting
    # path('planting/<int:pk>', PlantingDelete.as_view(), name='planting-delete'),
    path('folium_map/', folium_map, name='folium_map'),

    #get Ajax Data
    # path('parcelles/data', ParcellesView.as_view(), name="parcelles_data"),
    path('parcelle_list/', parcelle_list, name="parcelle_list"),
    path('parcelles_list/', ParcellesMapView.as_view(), name="parcelle_list"),

    #path('my-section/', my_section, name='my_section'),
    # path('ajax/load-section/', load_section, name='ajax_load_section'),

    #Exportation de Données En Excel
    # path('export/csv/', export_producteur_csv, name='export_producteur_csv'),
    path('producteurs/xls/', export_prod_xls, name='export_prod_xls'),
    path('sections/xls/', export_section_xls, name='export_section_xls'),
    path('sous_sections/xls/', export_sous_section_xls, name='export_sous_section_xls'),
    path('parcelles/xls/', export_parcelle_xls, name='export_parcelle_xls'),
    path('plants/xls/', export_plant_xls, name='export_plant_xls'),
    path('formations/xls/', export_formation_xls, name='export_formation_xls'),
    path('plantings/xls/', export_planting_xls, name='export_planting_xls'),

    #Export Données EN PDF
    path('producteurs/pdf/', export_prods_to_pdf, name='export_prods_to_pdf'),
    path('parcelles/pdf/', export_parcelles_to_pdf, name='export_parcelles_to_pdf'),


    path('parcelleCoop/<str:code>/', getParcelleCoop, name="parcelleCoop"),

    #route des parcelles par cooperative
    path('map_by_cooperative', map_by_cooperative, name="map_by_cooperative"),
    ######################################monitoring
    path('edit_monitoring_view/<str:code>/', edit_monitoring_view, name="edit_monitoring_view"),
    path('edit_monitoring', edit_monitoring, name="edit_monitoring"),
    path('edit_productor', edit_productor, name="edit_productor"),
    path('edit_formatoin/<int:id>', edit_formatoin, name="edit_formatoin"),
    path('update_formation', update_formation, name="update_formation"),
    path('parcelle_update', parcelle_update, name="parcelle_update"),
    path('edit_section/<int:id>', edit_section, name="edit_section"),
    path('update_section/', update_section, name='update_section'),
    path('edit_sous_section/<int:id>', edit_sous_section, name="edit_sous_section"),
    path('sous_section/', update_sous_section, name='update_sous_section'),
    path('monitoringSave/', monitoringSave, name='monitoringSave'),
    path('espece_monitoring_view/<str:code>', espece_monitoring_view, name='espece_monitoring_view'),
    path('plantingSave/', plantingSave, name='plantingSave'),
    path('producteurSave/', producteurSave, name='producteurSave'),
    path('parcelleSave/', parcelleSave, name='parcelleSave'),
    path('tranning/<int:id>', tranning, name='tranning'),
    path('saveParticipant/', saveParticipant, name='saveParticipant'),
    path('deletes/', deletes, name='deletes'),
    path('participant_delete/<int:id>', participant_delete, name='participant_delete'),
    path('formationSave/', formationSave, name='formationSave'),
    path('export_formation_to_pdf/<int:id>/', export_formation_to_pdf, name='export_formation_to_pdf'),
    path('changeSection/', changeSection, name='selectSection'),
    path('contactProd/', contactProd, name='contactProd'),
    path('remplacement_monitoring_view/<str:code>/', remplacement_monitoring_view, name='remplacement_monitoring_view'),
    path('RemplaceSave/', RemplaceSave, name='RemplaceSave'),
    path('endremplaceSave/', endremplaceSave, name='endremplaceSave'),
    path('esrempla_monitoring_view/<str:code>/', esrempla_monitoring_view, name='esrempla_monitoring_view'),
    path('rempend_monitoring_view/<str:code>/', rempend_monitoring_view, name='rempend_monitoring_view'),
    path('monitoring_form_view/<str:code>/', monitoring_form_view, name='monitoring_form_view'),
    path('deleteEspece/<str:code>/', deleteEspece, name='deleteEspece'),
    path('production/', production, name="productions"),
    path('productionSave/', productionSave, name="productionSave"),
    path('edit_product/<str:code>/', edit_product, name='edit_product'),
    path('production_delete/<str:code>/', production_delete, name='production_delete'),
    path('production_update/', production_update, name="production_update"),








   #####################API URL FLUTTER#######################

    ###PRODUCTEUR
    path('apiProdListCoop/<int:id>/',getProducteursForcoop,name='apilist_prod'),
    path('apiCreateProd/',createProducteurs,name='apicreate_prod'),
    path('apiUpdateProd/<int:id>/', updateProducteur, name='apiup_prod'),

    ###PARCELLE
    path('apiParcListCoop/',getListParcForcoop,name='apilist_parc'),
    path('apiCreateParc/',createParcelle,name='apicreate_parc'),

    ###PLANTING
    path('apiCreatePlant/',createPlanting,name='apicreate_plant'),
    path('apiCreatedetailPlant/',createDetailplanting,name='apicreate_detailplant'),

    ###MONITORING
    path('apiListMonitoring/',getMonitoringForcoop,name='apiget_moni'),
    path('apiCreateMonitoring/',monitoringCreate,name='apicreate_moni'),
    path('apiCreatedetailMonitoring/',createDetailmonitoring,name='apicreate_detailmoni'),
    path('apiCreateMonitoringespece/',createEspecemonitoring,name='apicreate_moniespece'),
    path('apiUpdateMonitoringespece/',updateMonitoring,name='apiupdate_moniespece'),
    path('apiObsMonitoring/',obsMonitoringFunc,name='api_obsmonitoring'),

   ################################################################## 28/06/2022 #######################MPI#######HISTORIQUE
    path('view_historique/',view_historique,name='view_historique'),
    path('consult_histo/',consult_histo,name='consult_histo'),
    
    ################################################## TEST ##############################
    path('saveProdFile/',saveProdFile,name='save_prod_file'),
    path('importValidProd/',importValidProd,name='importValidProd'),
    path('importAnnuleProd/',importAnnuleProd,name='importAnnuleProd'),
    
    ###################################################################DATATABLE ##########
    path('prod_table/',prodTableFunction,name='prodTable'),
    path('parc_table/',parcTableFunction,name='parcTable'),
    path('plant_table/',plantTableFunction,name='plantTable')
    

]