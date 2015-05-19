regattaApp
.controller('UploadController', function($scope, FileUploader) {
	$scope.hideSpinner = true;


	var uploader = $scope.uploader = new FileUploader({url: '/api/loadrml'});
	uploader.onCompleteItem = function(fileItem, response, status, headers) {
		console.info('onCompleteItem', fileItem, response, status, headers);
		$scope.status = "RML file processing complete.  Ready to go"
		$scope.hideSpinner = true;
	};
	uploader.onProgressItem = function(fileItem, progress) {
		console.info('onProgressItem', fileItem, progress);
	};
	uploader.onBeforeUploadItem = function(item) {
		$scope.hideSpinner = false;
		$scope.status = "Processing regatta file......this will take a minute	"
		console.info('onBeforeUploadItem', item);
	};
	uploader.onAfterAddingFile = function(fileItem) {
		console.info('onAfterAddingFile', fileItem);
		if ( uploader.queue.length > 1 ) {
			$scope.status = "Only upload 1 file"
			uploader.queue[1].remove();
		}
	};
});
