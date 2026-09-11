Hãy lùi lại một chút về quá khứ. Vì Collaboration Context (Ngữ cảnh Cộng tác) là Core Domain (Miền Lõi) đầu tiên, hãy cùng nhìn sâu vào bên trong nó. Trước tiên, chúng ta sẽ giới thiệu kỹ thuật "phóng to" (zooming) với các tích hợp đơn giản hơn, sau đó tiến dần tới các tích hợp nâng cao.

## Collaboration Context

Bây giờ, hãy quay trở lại với trải nghiệm của nhóm phát triển Collaboration . . .

Collaboration Context từng là mô hình và hệ thống đầu tiên — Core Domain (Miền Lõi - phần mang lại giá trị cạnh tranh cốt lõi nhất của doanh nghiệp) đầu tiên — và cơ chế hoạt động của nó hiện đã được hiểu rất rõ. Các tích hợp được áp dụng ở đây tương đối dễ triển khai nhưng lại kém vững chắc hơn xét về độ tin cậy và tính tự trị (autonomy). Việc xây dựng một Context Map (Bản đồ Ngữ cảnh - sơ đồ biểu diễn ranh giới và mối quan hệ giữa các Bounded Context) dạng phóng to được thực hiện khá dễ dàng.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000081_16199bc37a90797f5a635a78f3d3363aaddf323a405920cdd3e5b42fafec963f.png)

Với tư cách là một client (bên tiêu thụ dịch vụ) của các dịch vụ REST-based (dựa trên kiến trúc REST) do Identity and Access Context (Ngữ cảnh Định danh và Truy cập) phát hành, Collaboration Context tiếp cận tài nguyên theo phong cách tương tự như RPC (Remote Procedure Call - gọi thủ tục từ xa) truyền thống. Context này không lưu trữ vĩnh viễn bất kỳ dữ liệu nào từ Identity and Access Context để có thể tham chiếu tái sử dụng cục bộ sau đó. Thay vào đó, mỗi khi cần thông tin, nó lại gửi yêu cầu đến hệ thống từ xa. Context này hiển nhiên phụ thuộc rất lớn vào các dịch vụ từ xa, không hề có tính tự trị. Đây là thực tế mà SaaSOvation tạm thời chấp nhận sống chung ở thời điểm hiện tại. Việc phải tích hợp với một Generic Subdomain (Phân vùng miền Chung - phân vùng phụ trợ giải quyết bài toán nghiệp vụ phổ biến, không đặc thù) hoàn toàn nằm ngoài dự tính ban đầu. Nhằm đáp ứng lịch bàn giao dự án vô cùng gấp gáp, nhóm không thể đầu tư thời gian vào một thiết kế tự trị phức tạp hơn. Tại thời điểm đó, lợi thế thiết kế đơn giản, nhanh chóng từ đầu là một đặc quyền không thể bỏ lỡ. Sau khi ProjectOvation được triển khai thành công và tích lũy được nhiều kinh nghiệm về tính tự trị, các kỹ thuật tương tự có thể sẽ được áp dụng lại cho CollabOvation.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000082_01e66e3acfde39eee28b998735e189c2067120b94834901386a08e40f878e8ce.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000083_3ab52c7cba3fa7a8cbd68da71ad95e5e83e78c5ca93d1f0c11ffcf43e035bf96.png)

Các boundary objects (đối tượng ranh giới - đối tượng chịu trách nhiệm giao tiếp xuyên biên giới Context) trong Bản đồ phóng to được chụp ở Hình 3.6 gửi yêu cầu tài nguyên một cách đồng bộ (synchronously). Khi nhận được representation (biểu diễn dữ liệu) từ mô hình từ xa, các đối tượng ranh giới sẽ trích xuất nội dung cần quan tâm ra khỏi representation và thực hiện chuyển dịch (translate), từ đó tạo ra thực thể Value Object (Đối tượng Giá trị - đối tượng được định danh bằng thuộc tính chứ không có ID riêng) phù hợp. Một Translation Map (Bản đồ Chuyển dịch - lược đồ ánh xạ dữ liệu giữa hai mô hình) dùng để biến đổi representation thành một Value Object được thể hiện trong Hình 3.7. Tại đây, một User với Role (Vai trò) là Moderator trong Identity and Access Context sẽ được chuyển dịch thành Value Object Moderator trong Collaboration Context.

Hình 3.6 Phóng to vào Anticorruption Layer và Open Host Service trong phần tích hợp giữa Collaboration Context và Identity and Access Context

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000084_7f5d8c808b8cf15432613136a51951ed589c5f5eb76d549a59726814cb215233.png)

Hình 3.7 Một Translation Map ở mức logic thể hiện cách một trạng thái biểu diễn (ở đây là XML) được ánh xạ thành một Value Object trong mô hình cục bộ.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000085_9b739c792152222c96ab8148660b90fbedbd09c78c26c77c9e9d95d08eaa5e4d.png)

## Whiteboard Time

Hãy tạo một Translation Map cho một trong những khía cạnh tích hợp thú vị xuất hiện trong Bounded Context (Ngữ cảnh Ranh giới - ranh giới tường minh nơi một mô hình miền cụ thể được áp dụng) của dự án bạn.

Điều gì xảy ra nếu bạn nhận thấy các phép chuyển dịch quá phức tạp, đòi hỏi sao chép và đồng bộ hóa lượng dữ liệu khổng lồ, khiến đối tượng sau khi chuyển dịch trông giống hệt đối tượng từ mô hình ngoại lai? Rất có thể bạn đang phụ thuộc quá nhiều vào Bounded Context ngoại lai đó, tiếp nhận quá nhiều khái niệm từ mô hình của họ, và từ đó gây ra sự xung đột, rối loạn ngay bên trong mô hình của chính mình.

Thật không may, nếu yêu cầu đồng bộ bị thất bại do hệ thống từ xa không khả dụng, toàn bộ luồng thực thi cục bộ cũng bắt buộc phải thất bại theo. Người dùng sẽ được thông báo về sự cố và được yêu cầu thử lại sau.

Việc tích hợp giữa các hệ thống thường phụ thuộc vào RPC. Ở góc nhìn trừu tượng cấp cao, RPC trông rất giống một lệnh gọi hàm hay thủ tục lập trình thông thường. Các thư viện và công cụ khiến nó trở nên hấp dẫn và dễ sử dụng. Tuy nhiên, khác với việc gọi một thủ tục cư trú ngay trong cùng không gian tiến trình (process space), một lệnh gọi từ xa tiềm ẩn nguy cơ rất cao về độ trễ (latency) làm suy giảm hiệu năng hoặc hỏng hóc hoàn toàn. Tải của mạng và hệ thống từ xa có thể làm chậm trễ quá trình hoàn tất RPC. Khi hệ thống đích của RPC không khả dụng, yêu cầu của người dùng gửi đến hệ thống của bạn sẽ không thể hoàn thành thành công.

Mặc dù việc sử dụng tài nguyên dựa trên REST không hoàn toàn giống RPC, nó vẫn mang những đặc tính tương tự. Dù việc hệ thống sập hoàn toàn là tương đối hiếm, đây vẫn là một hạn chế tiềm ẩn gây phiền toái. Nhóm phát triển rất mong muốn sớm cải thiện tình trạng này ngay khi có thể.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000086_d91ebfe0645ea86d30a7c6fd6e096b5bb4ef5521147ff5232590e9eb544947ef.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000087_0f3415cc1c1714a7bec6b651e85b3af02d138ee1293e8212edf46e5c3bccf499.png)

## Agile Project Management Context

Vì Agile Project Management Context (Ngữ cảnh Quản lý Dự án Linh hoạt) là Core Domain mới, hãy dành sự quan tâm đặc biệt kỹ lưỡng cho nó. Hãy cùng phóng to vào nó và các liên kết giữa nó với những mô hình khác.

Để đạt được mức độ tự trị cao hơn so với những gì RPC mang lại, nhóm phát triển Agile Project Management Context cần phải hạn chế việc sử dụng RPC một cách cẩn trọng. Do đó, việc xử lý sự kiện bất đồng bộ hoặc ngoài luồng (out-of-band) được ưu tiên về mặt chiến lược.

Một mức độ tự trị cao hơn có thể đạt được khi trạng thái phụ thuộc (dependent state) đã sẵn sàng tồn tại ngay trong hệ thống cục bộ của chúng ta. Một số người có thể coi đây như một bộ nhớ đệm (cache) chứa toàn bộ các đối tượng phụ thuộc, nhưng khi áp dụng DDD (Domain-Driven Design - Thiết kế Hướng Miền), thực tế thường không phải như vậy. Thay vào đó, chúng ta tạo ra các domain objects (đối tượng miền) cục bộ được chuyển dịch từ mô hình ngoại lai, chỉ duy trì lượng trạng thái tối thiểu mà mô hình cục bộ thực sự cần. Để có được trạng thái này ngay từ đầu, chúng ta có thể thực hiện một số lệnh gọi RPC giới hạn và được tính toán kỹ lưỡng, hoặc các yêu cầu tương tự đối với các tài nguyên REST. Tuy nhiên, bất kỳ sự đồng bộ hóa cần thiết nào đối với các thay đổi từ mô hình từ xa thường được thực hiện tốt nhất thông qua các thông báo hướng thông điệp (message-oriented notifications) do hệ thống từ xa phát hành. Các thông báo này có thể được gửi qua một service bus, message queue (hàng đợi thông điệp), hoặc phát hành qua REST.

## Think Minimalistic

Trạng thái được đồng bộ hóa chỉ là các thuộc tính giới hạn, tối thiểu từ các mô hình từ xa mà mô hình cục bộ thực sự cần. Điều này không chỉ nhằm hạn chế nhu cầu đồng bộ dữ liệu, mà còn là vấn đề mô hình hóa các khái niệm sao cho chuẩn xác.

Việc hạn chế sử dụng trạng thái từ xa luôn đem lại lợi ích, ngay cả khi cân nhắc thiết kế cho chính các thành phần mô hình hóa cục bộ. Ví dụ, chúng ta không bao giờ muốn ProductOwner và TeamMember trên thực tế lại biến thành bản sao phản chiếu của UserOwner và UserMember chỉ vì chúng tiếp nhận quá nhiều đặc tính từ đối tượng User từ xa, dẫn đến việc bị lai tạp (hybridization) một cách vô thức.

## Integration with the Identity and Access Context

Quan sát Bản đồ phóng to trong Hình 3.8, chúng ta thấy rằng các URI (Uniform Resource Identifier - chuỗi định danh tài nguyên) tài nguyên cung cấp các thông báo về các Domain Events (Sự kiện Miền - sự kiện nghiệp vụ quan trọng đã xảy ra trong quá khứ của miền nghiệp vụ) quan trọng đã phát sinh trong Identity and Access Context. Những thông báo này được cung cấp thông qua nhà cung cấp NotificationResource — nơi phát hành một RESTful resource. Các tài nguyên thông báo là các nhóm chứa những Domain Event đã phát hành. Mọi Event từng được công bố đều luôn sẵn sàng để tiêu thụ theo đúng thứ tự phát sinh, nhưng mỗi client phải tự chịu trách nhiệm ngăn chặn việc tiêu thụ trùng lặp (duplicate consumption).

Một custom media type (kiểu định dạng phương tiện tùy chỉnh) cho biết có hai tài nguyên có thể được yêu cầu:

application/vnd.saasovation.idovation+json

//iam/notifications

//iam/notifications/{notificationId}

Hình 3.8 Phóng to vào Anticorruption Layer và Open Host Service trong tích hợp giữa Agile Project Management Context và Identity and Access Context

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000088_d4be8e79a6fa569ab42996c2f28282d82ab2ef52e15bc2a56e1d605a72d1daed.png)

URI tài nguyên đầu tiên cho phép các client lấy về (theo đúng nghĩa HTTP GET) notification log (nhật ký thông báo) hiện tại (một tập hợp cố định các thông báo riêng lẻ). Theo custom media type đã được tài liệu hóa:

application/vnd.saasovation.idovation+json

URI này được coi là đã được đúc cố định (minted) và có tính ổn định cao vì nó không bao giờ thay đổi. Bất kể log thông báo hiện tại bao gồm những gì, URI này đều cung cấp nó. Log hiện tại là tập hợp các sự kiện gần đây nhất vừa xảy ra trong mô hình Identity and Access. URI tài nguyên thứ hai cho phép client lấy và duyệt theo chuỗi tất cả các thông báo dựa trên sự kiện trước đó đã được lưu trữ (archived). Tại sao chúng ta lại cần một log hiện tại và một số lượng tùy ý các log thông báo lưu trữ riêng biệt? Xem Domain Events (Chương 8) và Integrating Bounded Contexts (Chương 13) để biết chi tiết về cách thức hoạt động của các thông báo dạng nguồn cấp (feed-based notifications).

Thực tế, tại thời điểm này, nhóm ProjectOvation chưa hoàn toàn cam kết sử dụng REST trong mọi trường hợp. Ví dụ, họ hiện đang đàm phán với nhóm CollabOvation về việc liệu có nên sử dụng hạ tầng messaging (truyền thông điệp) thay thế hay không.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000089_a8d26a05f2d2bc628ea24c053528e8a3b814e5582d4c9e82ba5ba9526c62fe53.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000090_e149e8269e955cf50f43413a1ef54b07a64b8f9c3b9b5a8515bf9fe501ef8a3a.png)

Phương án sử dụng RabbitMQ đang được đưa ra cân nhắc. Mặc dù vậy, ở thời điểm hiện tại, các tích hợp của họ với Identity and Access Context vẫn sẽ dựa trên REST.

Tạm thời gác lại hầu hết các chi tiết công nghệ, hãy cùng xem xét vai trò của từng đối tượng tương tác trong Bản đồ phóng to. Dưới đây là phần giải thích cho các bước tích hợp được minh họa trực quan trong biểu đồ tuần tự (sequence diagram) ở Hình 3.9:

- MemberService là một Domain Service (Dịch vụ Miền - dịch vụ thực thi logic nghiệp vụ không thuộc về một Entity hay Value Object cụ thể nào) chịu trách nhiệm cung cấp các đối tượng ProductOwner và TeamMember cho mô hình cục bộ của nó. Nó đóng vai trò là interface (giao diện) của Anticorruption Layer (Lớp Chống Tha hóa - lớp trung gian cô lập và biên dịch giúp mô hình nội bộ không bị ảnh hưởng bởi mô hình bên ngoài) cơ bản. Cụ thể, phương thức maintainMembers() được gọi định kỳ để kiểm tra các thông báo mới từ Identity and Access Context. Phương thức này không được gọi bởi các client thông thường của mô hình. Khi một chu kỳ hẹn giờ (timer interval) kích hoạt, thành phần nhận thông báo sẽ sử dụng MemberService bằng cách gọi phương thức maintainMembers(). Hình 3.9 thể hiện thành phần nhận sự kiện hẹn giờ là MemberSynchronizer, đối tượng này ủy quyền xử lý cho MemberService.
- MemberService ủy quyền cho IdentityAccessNotificationAdapter, đóng vai trò là Adapter (bộ chuyển đổi) giữa Domain Service và Open Host Service (Dịch vụ Máy chủ Mở - giao thức/giao diện công khai chuẩn hóa cho phép các hệ thống khác tích hợp) của hệ thống từ xa. Adapter đóng vai trò như một client đối với hệ thống từ xa. Sự tương tác với NotificationResource từ xa không được hiển thị trong sơ đồ.
- Khi Adapter nhận được phản hồi từ Open Host Service từ xa, nó ủy quyền cho MemberTranslator để chuyển dịch Published Language (Ngôn ngữ Xuất bản - định dạng dữ liệu chuẩn dùng chung để trao đổi giữa các ngữ cảnh) sang các khái niệm của hệ thống cục bộ. Nếu thực thể Member cục bộ đã tồn tại, quá trình chuyển dịch sẽ cập nhật đối tượng miền hiện có. Điều này được thể hiện bằng việc MemberService tự ủy quyền nội bộ tới phương thức updateMember() của chính nó. Các lớp con của Member là ProductOwner và TeamMember, phản ánh chính xác các khái niệm trong ngữ cảnh cục bộ.

Hình 3.9 Góc nhìn về cơ chế hoạt động bên trong của Anticorruption Layer giữa Agile Project Management Context và Identity and Access Context

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000091_b4493904ee096207e88a28bd88b93686475fe21ffff71a193381cf9fc30f1333.png)

Chúng ta không nên quá tập trung vào các công nghệ hay sản phẩm tích hợp liên quan. Thay vào đó, bằng cách phân tách rành mạch các Bounded Context, chúng ta có thể giữ cho mỗi Context luôn thuần khiết, trong khi vẫn tiếp nhận dữ liệu từ các Context khác để biểu đạt các khái niệm trong mô hình của chính mình.

Các sơ đồ và văn bản bổ trợ là ví dụ điển hình về cách chúng ta tạo lập các tài liệu Context Map. Tài liệu này không cần quá đồ sộ, nhưng phải cung cấp đủ bối cảnh nền tảng và lời giải thích để giúp một thành viên mới của dự án nhanh chóng nắm bắt công việc. Tuy nhiên, chỉ nên tạo tài liệu nếu nó thực sự mang lại giá trị hữu ích cho nhóm.

Tích hợp với Collaboration Context: Tiếp theo, hãy xem xét cách Agile Project Management Context tương tác với Collaboration Context. Ở đây, chúng ta cũng nỗ lực hướng tới tính tự trị, nhưng yêu cầu này đã nâng tiêu chuẩn lên cao hơn, đặt ra một số thách thức thú vị để đạt được mục tiêu độc lập giữa các hệ thống.

ProjectOvation có các tính năng mở rộng (add-on) được cung cấp bởi CollabOvation. Một số tính năng có thể kể đến như thảo luận diễn đàn theo dự án và lập lịch chia sẻ lịch biểu. Người dùng sẽ không tương tác trực tiếp với CollabOvation. ProjectOvation phải xác định xem các tùy chọn đó có khả dụng cho một tenant (khách thuê/đơn vị thuê bao hệ thống đa người dùng) nhất định hay không, và nếu có, nó phải tự mình điều phối việc khởi tạo tài nguyên bên trong CollabOvation.

Hãy xem xét một phần của use case (trường hợp sử dụng) Create a Product (Tạo Sản phẩm) dưới đây:

Điều kiện tiên quyết: Tính năng cộng tác đã được kích hoạt (tùy chọn này đã được mua).

1. Người dùng cung cấp thông tin mô tả Sản phẩm (Product).
2. Người dùng bày tỏ mong muốn có một cuộc thảo luận nhóm.
3. Người dùng yêu cầu tạo Sản phẩm đã định nghĩa.
4. Hệ thống tạo Sản phẩm kèm theo một Diễn đàn (Forum) và Cuộc thảo luận (Discussion).

Một Forum và một Discussion phải được tạo bên trong Collaboration Context thay mặt cho Product. Ngược lại, điều này hoàn toàn khác với Identity and Access Context — nơi một tenant vốn đã được cấp phát, người dùng, nhóm và vai trò đã được định nghĩa từ trước, và các thông báo về các sự kiện đó luôn có sẵn. Trong trường hợp đó, các đối tượng đã tồn tại từ trước. Nhưng trong trường hợp này, Agile Project Management Context cần những đối tượng chưa hề tồn tại và sẽ không thể tồn tại cho đến khi nó gửi yêu cầu tạo. Đó là một trở ngại tiềm tàng đối với tính tự trị vì chúng ta phụ thuộc vào tính sẵn sàng của Collaboration Context để tạo tài nguyên từ xa. Với mong muốn đạt được tính tự trị, điều này đặt ra một thách thức rất đáng quan tâm.

## Why Is Discussion Used in Both Contexts?

Đây là một tình huống rất thú vị vì tên của khái niệm — Discussion — hoàn toàn giống nhau ở cả hai Bounded Context, nhưng chúng là các kiểu (types) khác nhau, các đối tượng khác nhau, và do đó mang trạng thái cùng hành vi hoàn toàn khác nhau.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000092_199ca21c5e687641fda97b800dcc917ff54834563db0b5a1c54c384c9e2a3176.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000093_096f296c186f753ae93a7dc733fd07332958add5f389f5aac7c8cd3d585779f3.png)

Trong Collaboration Context, một Discussion là một Aggregate (Cụm Tổng hợp - một nhóm các thực thể và đối tượng giá trị gắn kết chặt chẽ được coi như một đơn vị đồng nhất khi thay đổi dữ liệu) và nó quản lý một tập hợp các Post (Bài đăng) — các đối tượng con ngầm định mà bản thân chúng cũng là các Aggregate. Còn trong Agile PM Context, Discussion chỉ là một Value Object và nó chỉ nắm giữ một tham chiếu tới Discussion thực sự chứa các Post nằm ở Context ngoại lai kia. Tuy nhiên, cần lưu ý rằng trong Chương 13, khi nhóm bắt tay triển khai phần tích hợp, họ phát hiện ra rằng họ nên tạo các kiểu strongly typed (định kiểu mạnh) cho các loại Discussion khác nhau trong Agile PM Context.

Chúng ta cần tận dụng tính nhất quán sau cùng (eventual consistency) thông qua việc sử dụng Domain Events (Chương 8) và Event-Driven Architecture (Kiến trúc Hướng Sự kiện - Chương 4). Không có bất kỳ quy định nào bắt buộc rằng chỉ các hệ thống từ xa mới được phép tiêu thụ các thông báo do hệ thống cục bộ phát ra. Khi một Domain Event có tên ProductInitiated được mô hình của chúng ta xuất bản, nó sẽ được xử lý bởi chính hệ thống của chúng ta. Handler (bộ xử lý) cục bộ sẽ yêu cầu Forum và Discussion được khởi tạo từ xa. Việc này có thể được thực hiện qua RPC hoặc messaging, tùy thuộc vào những gì CollabOvation hỗ trợ. Nếu sử dụng RPC mà hệ thống cộng tác từ xa lúc đó lại không khả dụng, handler cục bộ sẽ chỉ đơn giản tiếp tục thử lại định kỳ cho đến khi thành công. Nếu messaging được hỗ trợ thay vì RPC, handler cục bộ sẽ gửi một message đến hệ thống cộng tác. Đổi lại, hệ thống cộng tác sẽ phản hồi bằng một message của chính nó khi quá trình tạo tài nguyên hoàn tất. Khi Event handler phía ProjectOvation nhận được thông báo này, nó sẽ cập nhật Product với một định danh tham chiếu (identity reference) trỏ tới cuộc thảo luận vừa được tạo.

Điều gì xảy ra nếu product owner hoặc các thành viên trong nhóm cố gắng sử dụng cuộc thảo luận trước khi nó thực sự tồn tại? Liệu một cuộc thảo luận chưa khả dụng có bị coi là một lỗi (bug) trong mô hình hay không? Liệu nó có khiến hệ thống rơi vào trạng thái thiếu tin cậy? Hãy cân nhắc thực tế rằng một thuê bao bất kỳ có thể ngay từ đầu đã không trả phí để sử dụng gói mở rộng cộng tác. Đó là một lý do phi kỹ thuật hoàn toàn chính đáng để thiết kế tính năng không khả dụng của tài nguyên. Việc xử lý tương thích với tính nhất quán sau cùng hoàn toàn không phải là một giải pháp chắp vá tạm bợ (kludge). Đó đơn giản chỉ là một trạng thái hợp lệ khác cần được đưa vào mô hình hóa.

Một cách thanh lịch để xử lý tất cả các kịch bản không khả dụng có thể xảy ra là biểu đạt chúng một cách tường minh. Hãy xem xét Standard Type (Kiểu Chuẩn) này được triển khai dưới dạng State (Mẫu Trạng thái) [Gamma et al.], như được mô tả trong Value Objects (Chương 6):

```java
public enum DiscussionAvailability {
    ADD_ON_NOT_ENABLED,
    NOT_REQUESTED,
    REQUESTED,
    READY;
}

public final class Discussion implements Serializable {
    private DiscussionAvailability availability;
    private DiscussionDescriptor descriptor;
    ...
}

public class Product extends Entity {
    ...

```

```java
    private Discussion discussion;
    ...
}

```

Sử dụng thiết kế này, Value Object Discussion được bảo vệ khỏi việc sử dụng sai mục đích nhờ State được định nghĩa bởi DiscussionAvailability che chắn cho nó. Khi ai đó cố gắng tham gia vào một cuộc thảo luận về Product, nó có thể bàn giao State thảo luận một cách an toàn. Nếu trạng thái không phải là READY, người tham gia sẽ nhìn thấy một trong ba thông báo:

> Để sử dụng tính năng cộng tác nhóm, bạn cần mua tùy chọn mở rộng.

> Product owner đã không yêu cầu tạo cuộc thảo luận cho sản phẩm này.

> Việc thiết lập cuộc thảo luận vẫn chưa hoàn tất; vui lòng quay lại sau.

Nếu độ khả dụng của Discussion là READY, chúng ta cho phép các thành viên trong nhóm tham gia đầy đủ.

Một điểm thú vị là, như thông điệp trạng thái không khả dụng đầu tiên ngụ ý, hoàn toàn có khả năng phía kinh doanh chủ động lựa chọn hiển thị các tùy chọn cộng tác cho phép người dùng chọn dù họ chưa hề mua chúng. Việc để các tùy chọn UI cộng tác ở trạng thái hiển thị có thể là một chiêu thức tiếp thị gợi nhắc (marketing tickler) đầy hiệu quả nhằm thúc đẩy việc mua hàng tiếp theo. Còn ai có thể thúc giục ban quản lý mua thêm tùy chọn mở rộng tốt hơn chính những nhân viên hàng ngày liên tục được nhắc nhở rằng họ có thể sử dụng tính năng đó, nhưng hiện tại thì chưa thể? Rõ ràng, lợi ích kỹ thuật không phải là điều duy nhất đạt được từ việc sử dụng State biểu thị độ khả dụng này.

Tại thời điểm này, nhóm phát triển vẫn chưa chắc chắn phương thức tích hợp thực tế với hệ thống cộng tác sẽ là gì. Để phục vụ cho các cuộc thảo luận theo mối quan hệ Customer-Supplier (Khách hàng - Nhà cung cấp), họ đã phác thảo sơ đồ trong Hình 3.10. Agile Project Management Context có thể sử dụng một Anticorruption Layer thứ hai để quản lý tích hợp giữa chính nó và Collaboration Context. Nó sẽ tương tự như lớp đã dùng cho Identity and Access Context. Sơ đồ hiển thị các boundary objects chính, tương tự như các đối tượng tương ứng được dùng cho việc tích hợp quản lý định danh và truy cập. Trên thực tế, không chỉ có duy nhất một CollaborationAdapter đơn lẻ. Nó chỉ là đối tượng giữ chỗ (placeholder) đại diện cho nhiều adapter khác cần thiết nhưng chưa được xác định cụ thể lúc này.

Được biểu diễn bên trong Context cục bộ là DiscussionService và SchedulingService. Chúng đại diện cho các Domain Service có thể được dùng để quản lý các cuộc thảo luận và các mục lịch biểu trong hệ thống cộng tác. Cơ chế thực tế sẽ được định đoạt thông qua các cuộc đàm phán Customer-Supplier giữa hai nhóm, được hiện thực hóa trong phần Integrating Bounded Contexts (Chương 13).

Nhóm hiện đã có thể hiểu được một phần mô hình của mình. Ví dụ, điều gì sẽ xảy ra khi một cuộc thảo luận đã được tạo và kết quả được truyền đạt lại cho Context cục bộ? Thành phần bất đồng bộ — có thể là RPC client hoặc message handler — sẽ gọi lệnh attachDiscussion() trên Product, truyền vào một thực thể Value mới của Discussion. Tất cả các Aggregate cục bộ đang chờ đợi tài nguyên từ xa đều sẽ được chăm sóc và xử lý theo cùng một cơ chế như vậy.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000094_d8e360f94fdf150686ebdd35fb34767265318dde0773d0dd336266cb025b7aeb.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000095_1332e1b5f33f31b1c8588a8a1aa99945e7d2a72ecb645171c4fcf0e635f870aa.png)

Hình 3.10 Phóng to vào một Anticorruption Layer và Open Host Service thuộc các thành phần tích hợp khả dĩ giữa Agile Project Management Context và Collaboration Context

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000096_319392cf0160f8840a14e98a62e6e713bec753188f3b5fba8c9a604a2e9b6aed.png)

Khảo sát này đã đi sâu vào một số chi tiết hữu ích về Context Map. Tuy nhiên, chúng ta cần phải biết kiềm chế, bởi vì chúng ta có thể nhanh chóng chạm tới điểm giới hạn mà lợi ích thu về giảm dần (diminishing returns). Có lẽ chúng ta đã có thể đưa cả Modules (Mô-đun - Chương 9) vào đây, nhưng chúng đã được bố trí trong một chương chuyên biệt riêng. Hãy chỉ đưa vào bất kỳ yếu tố cấp cao nào có liên quan giúp thúc đẩy sự giao tiếp sống còn trong nhóm. Mặt khác, hãy kiên quyết đẩy lùi những chi tiết mang nặng tính hình thức rườm rà.

Hãy tạo ra những Context Map mà bạn có thể in ra và dán ngay lên tường. Bạn có thể tải chúng lên wiki của nhóm, miễn sao wiki đó không biến thành "căn gác xép" bỏ hoang của dự án nơi chẳng bao giờ có ai bước chân vào. Hãy liên tục đưa các cuộc thảo luận về dự án đối chiếu trở lại với Bản đồ của bạn để kích thích những tinh chỉnh hữu ích.

> 💡 **Giải thích thêm:** Tác giả dùng ẩn dụ "project's attic" (căn gác xép của dự án) để cảnh báo về hiện tượng "documentation rot" (tài liệu bị lãng quên/lỗi thời). Tài liệu wiki nội bộ thường được viết rất hoành tráng lúc đầu nhưng sau đó không ai cập nhật hay đọc tới, biến thành nơi lưu trữ vô dụng. Bản đồ ngữ cảnh chỉ có giá trị khi nó là tài liệu sống (living document) được nhóm thường xuyên nhìn thấy và thảo luận.
> Nguồn tham khảo: [Martin Fowler - Living Documentation](https://www.google.com/search?q=https://martinfowler.com/bliki/LivingDocumentation.html)

## Wrap-Up

Đó chắc chắn là một buổi làm việc đầy hiệu quả về Context Mapping.

* Chúng ta đã thảo luận về bản chất của Context Map, những lợi ích chúng mang lại cho nhóm của bạn, và cách bạn có thể tạo ra chúng một cách dễ dàng.
* Bạn đã có một cái nhìn chi tiết vào ba Bounded Context của SaaSOvation cùng các Context Map bổ trợ của chúng.
* Sử dụng kỹ thuật lập bản đồ, bạn đã phóng to vào các điểm tích hợp giữa từng Context với nhau.
* Bạn đã kiểm tra các boundary objects hỗ trợ cho Anticorruption Layer cùng các tương tác của chúng.
* Bạn đã thấy cách tạo ra một Translation Map thể hiện sự ánh xạ cục bộ giữa các tài nguyên dựa trên REST và đối tượng tương ứng trong mô hình miền tiêu thụ.

Không phải dự án nào cũng cần mức độ chi tiết như được trình bày ở đây. Một số dự án khác có thể đòi hỏi nhiều hơn. Bí quyết nằm ở chỗ cân bằng giữa nhu cầu thấu hiểu với tính thực tế, không nhồi nhét quá nhiều chi tiết vụn vặt vào cấp độ này. Hãy nhớ rằng chúng ta nhiều khả năng sẽ không duy trì một Bản đồ đồ họa quá chi tiết trong suốt chặng đường dài của dự án. Chúng ta sẽ hưởng lợi nhiều nhất từ những gì có thể dán lên tường, giúp các thành viên trong nhóm có thể chỉ tay vào đó trong các cuộc thảo luận. Nếu chúng ta từ chối sự lễ nghi hình thức và đón nhận sự đơn giản cùng tính linh hoạt (agility), chúng ta sẽ tạo ra những Context Map hữu ích, giúp dự án tiến bước thay vì bị sa lầy.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000097_763821da2dc668f93e792c38b9e2f181e31501452a0d9e3833f3d1b92d5e65d6.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000098_dcdf334bcab59567ceb638822604c11adc7c51eb46179add29b50554284f96b5.png)

Trang này được cố tình để trống

## Chapter 4

## Architecture

> Kiến trúc phải nói lên được thời gian và không gian của nó, nhưng vẫn phải khao khát sự trường tồn vượt thời gian.
> — Frank Gehry

Một trong những ưu điểm lớn nhất của DDD là nó không đòi hỏi phải sử dụng bất kỳ một kiến trúc cụ thể nào. Vì Core Domain (Chương 2) được chúng ta trau chuốt kỹ lưỡng nằm ở trung tâm của một Bounded Context (Chương 2), nó cho phép một hoặc nhiều ảnh hưởng kiến trúc cùng đóng vai trò trong toàn bộ ứng dụng hoặc hệ thống. [^1] Một số ảnh hưởng kiến trúc bao bọc lấy mô hình miền và tạo ra tác động bao quát trên diện rộng, trong khi những ảnh hưởng khác lại giải quyết các nhu cầu cụ thể. Mục tiêu là đưa ra các lựa chọn và kết hợp chuẩn xác giữa kiến trúc và các architecture pattern (mẫu kiến trúc - giải pháp cấp hệ thống giải quyết một bài toán tổ chức phần mềm cụ thể).

Chính các đòi hỏi thực tế về những phẩm chất phần mềm cụ thể phải là yếu tố dẫn dắt việc sử dụng các phong cách kiến trúc (architectural styles) và mẫu kiến trúc. Những lựa chọn được đưa ra phải chứng minh được khả năng đáp ứng hoặc vượt trên cả các phẩm chất yêu cầu đó. Việc tránh lạm dụng phong cách kiến trúc và mẫu kiến trúc cũng quan trọng không kém gì việc sử dụng đúng loại. Để các yêu cầu chất lượng thực sự dẫn dắt các quyết định kiến trúc là một phương pháp tiếp cận hướng rủi ro (risk-driven approach) đầy lợi ích [Fairbanks]. Bằng cách đó, chúng ta chỉ sử dụng kiến trúc để giảm thiểu rủi ro thất bại, chứ không làm gia tăng rủi ro thất bại bằng việc đưa vào một phong cách hoặc mẫu kiến trúc không thể biện minh được tính cần thiết. Do đó, chúng ta phải có khả năng chứng minh được sự hợp lý của từng ảnh hưởng kiến trúc đang sử dụng, nếu không, hãy loại bỏ nó khỏi hệ thống.

Khả năng chứng minh tính hợp lý khi lựa chọn bất kỳ phong cách và mẫu kiến trúc nào của chúng ta phụ thuộc hoàn toàn vào các yêu cầu chức năng sẵn có, chẳng hạn như use cases hoặc user stories (câu chuyện người dùng), và thậm chí cả các kịch bản đặc thù của mô hình miền. Nói cách khác, bạn không thể xác định các phẩm chất phần mềm cần thiết nếu thiếu đi các yêu cầu chức năng. Thiếu những đầu vào dạng này, chúng ta thực sự không thể đưa ra các lựa chọn kiến trúc đúng đắn, điều đó hàm ý rằng việc áp dụng cách tiếp cận kiến trúc hướng use-case (use-case-driven architecture approach) vào phát triển phần mềm vẫn hoàn toàn nguyên giá trị cho đến tận ngày nay.

[^1]: Chương này bàn về các phong cách kiến trúc (architectural styles), kiến trúc ứng dụng (application architectures), và các mẫu kiến trúc (architecture patterns). Một phong cách sẽ mô tả cách thức hiện thực hóa một kiến trúc cụ thể, trong khi một mẫu kiến trúc giải thích cách giải quyết một mối bận tâm cụ thể bên trong kiến trúc nhưng có phạm vi rộng lớn hơn một mẫu thiết kế (design pattern). Tôi khuyên bạn không nên quá câu nệ vào sự khác biệt giữa các khái niệm này, mà chỉ cần hiểu rằng DDD có thể nằm ở vị trí trung tâm của rất nhiều ảnh hưởng kiến trúc bao bọc xung quanh.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000099_d2719ff7e77ddc31a7d0ed285d455cdec2f11b8f92de6693338813cac1587761.png)

## Road Map to This Chapter

* Lắng nghe buổi phỏng vấn nhìn lại chặng đường đã qua với Giám đốc Thông tin (CIO) của SaaSOvation.
* Tìm hiểu cách thức mà Kiến trúc Phân tầng (Layers Architecture) đáng tin cậy đã được cải tiến nhờ DIP và Hexagonal.
* Xem cách Hexagonal có thể hỗ trợ Kiến trúc Hướng Dịch vụ (Service-Oriented) và REST.
* Đạt được góc nhìn toàn diện về phong cách Data Fabric hoặc Grid-Based Distributed Cache (Bộ nhớ đệm phân tán dạng lưới) và Kiến trúc Hướng Sự kiện (Event-Driven).
* Xem xét cách một mẫu kiến trúc mới hơn có tên gọi CQRS hỗ trợ đắc lực cho DDD.
* Học hỏi từ các kiến trúc thực tế được các nhóm phát triển tại SaaSOvation áp dụng.

## Architecture Isn't a Coolness Factor

Các phong cách và mẫu kiến trúc sau đây không phải là một túi đồ chơi công nghệ hấp dẫn để chúng ta tiện tay áp dụng bừa bãi vào mọi nơi có thể. Thay vào đó, hãy chỉ sử dụng chúng ở những nơi thực sự thích hợp, nơi chúng giúp giảm thiểu một rủi ro cụ thể mà nếu không giải quyết sẽ làm tăng khả năng thất bại của dự án hoặc hệ thống.

[Evans] tập trung vào Layers Architecture. Chính vì vậy, SaaSOvation thoạt đầu đã vội vã kết luận rằng DDD chỉ có thể phát huy hiệu quả khi sử dụng mẫu kiến trúc nổi tiếng đó. Các nhóm đã phải mất một thời gian mới hiểu ra rằng DDD có khả năng thích ứng linh hoạt hơn thế rất nhiều, mặc dù Layers là mẫu thịnh hành nhất vào thời điểm cuốn sách của [Evans] được viết.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000100_71b5d40adb3d20ae593f4990a35395268a6e4f74e28391858b3ba73f52a5ee3d.png)

Các nguyên lý của Layers Architecture vẫn có thể được vận dụng để định hướng cho những quyết định đúng đắn. Tuy nhiên, chúng ta không cần dừng lại ở đó, bởi vì chúng ta sẽ xem xét một số kiến trúc và mẫu hiện đại hơn có thể được tận dụng khi cần. Điều này sẽ chứng minh tính đa năng và khả năng áp dụng rộng rãi của DDD.

Chắc chắn rằng, SaaSOvation không cần đến mọi ảnh hưởng kiến trúc cùng một lúc, nhưng các nhóm của họ cần phải đưa ra những lựa chọn khôn ngoan từ các phương án sẵn có.

## Interviewing the Successful CIO

Để mang lại góc nhìn rõ nét hơn về lý do tại sao từng ảnh hưởng kiến trúc được thảo luận trong chương này lại được áp dụng, chúng ta sẽ bước một bước nhảy vọt mười năm tới tương lai và trò chuyện với CIO của SaaSOvation. Dù công ty có khởi đầu khiêm tốn, các quyết định kiến trúc chuẩn xác đã giúp công ty gặt hái thành công trên từng chặng đường. Hãy cùng theo dõi chương trình TechMoney với người dẫn chương trình Maria Finance-Ilmundo . . .

Maria: Tối nay, buổi phỏng vấn độc quyền của tôi sẽ diễn ra với Mitchell Williams, CIO của công ty SaaSOvation vô cùng thành công. Chúng tôi đang tiếp tục loạt phóng sự "Hiểu đúng về Phong cách Kiến trúc của bạn" (Know Your Architectural $tyles). Trọng tâm tối nay là cách thức việc lựa chọn kiến trúc phù hợp có thể mang lại thành công bền vững. Chào mừng anh đến với chương trình, Mitchell, và cảm ơn anh đã tham gia cùng chúng tôi.

Mitchell: Tôi rất vui được gặp lại cô ở đây, Maria. Luôn luôn là một niềm vinh hạnh.

Maria: Anh có thể điểm qua một vài quyết định kiến trúc ban đầu mà các anh đã lựa chọn, và lý do tại sao không?

Mitchell: Tất nhiên rồi. Dù tin hay không, chúng tôi thực sự đã bắt đầu lên kế hoạch cho các dự án của mình xoay quanh việc triển khai ứng dụng desktop. Nhóm của chúng tôi đã thiết kế để ứng dụng desktop lưu trữ dữ liệu vào một cơ sở dữ liệu tập trung. Họ đã chọn Layers Architecture cho cách tiếp cận này.

Maria: Lựa chọn đó có hợp lý không?

Mitchell: Ồ, chúng tôi tin là có, đặc biệt là khi chúng tôi chỉ làm việc với một tầng ứng dụng (application tier) đơn lẻ cộng với cơ sở dữ liệu trung tâm. Nó phục vụ rất tốt cho một phong cách client-server đơn giản.

Maria: Nhưng tình thế đã sớm đảo chiều, phải không anh?

Mitchell: Chắc chắn là như vậy rồi. Chúng tôi thực tế đã bắt tay hợp tác với một đối tác kinh doanh và quyết định chuyển hướng sang mô hình thuê bao SaaS (Software as a Service - Phần mềm dưới dạng Dịch vụ). Chúng tôi đã tìm kiếm một khoản vốn tài trợ đáng kể để hỗ trợ các nỗ lực của mình và đã gọi vốn thành công. Chúng tôi xác định rằng ứng dụng quản lý dự án linh hoạt (agile project management) sẽ tạm thời phải gác lại một thời gian cho đến khi chúng tôi phát triển xong một bộ công cụ cộng tác trước. Điều này đem lại lợi ích kép: thứ nhất, chúng tôi sẽ thâm nhập vào thị trường cộng tác trực tuyến đang tăng trưởng nóng, nhưng thứ hai, chúng tôi cũng sẽ có sẵn một tính năng bổ trợ tự nhiên cho ứng dụng quản lý dự án. Cô biết đấy, cộng tác xung quanh các sản phẩm bàn giao của dự án phát triển phần mềm.

Maria: Thú vị thật. Mọi thứ nghe rất mộc mạc và thực tế từ gốc rễ. Những quyết định đó đã dẫn các anh đến đâu?

Mitchell: Khi độ phức tạp của phần mềm tăng lên, chúng tôi cần quản lý chất lượng bằng cách đưa vào các công cụ unit test (kiểm thử đơn vị) và feature test (kiểm thử tính năng). Để làm được điều đó, chúng tôi gần như đã đảo lộn hoàn toàn mô hình Layers bằng cách áp dụng Dependency Inversion Principle (Nguyên lý Đảo ngược Phụ thuộc), hay DIP. Việc này rất quan trọng vì nhóm có thể dễ dàng kiểm thử bằng cách tạo stub (mô phỏng dữ liệu phản hồi) cho User Interface Layer và Infrastructure Layer để tập trung kiểm thử Application Layer và Domain Layer. Trên thực tế, chúng tôi có thể phát triển giao diện người dùng (UI) một cách độc lập hoàn toàn và trì hoãn các quyết định về công nghệ lưu trữ dữ liệu (persistence) trong một thời gian khá dài. Và điều này thực ra không phải là một bước nhảy quá xa rời khỏi Layers. Nhóm cảm thấy rất thoải mái và tự tin.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000101_9a9846241849e24560f62ddcbe898144d1708713956b9ef84ac3762d82aebf5f.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000102_08d810112272525510218b39c53795f5b45b05489f0cf79b8387a3c31233ecfb.png)

Maria: Chà, hoán đổi cả UI lẫn tầng lưu trữ dữ liệu! Nghe có vẻ rủi ro đấy chứ. Việc đó có khó khăn lắm không?

Mitchell: À, thực ra thì không hề khó khăn chút nào. Hóa ra, việc chúng tôi áp dụng các tactical patterns (mẫu chiến thuật - các mẫu thiết kế cụ thể ở mức code trong DDD như Entity, Value Object, Aggregate) của Domain-Driven Design đã không hề gây cản trở mà còn hỗ trợ chúng tôi tối đa. Nhờ sử dụng mẫu Aggregate và Repository (Kho lưu trữ - đối tượng trừu tượng hóa việc truy xuất và lưu trữ Aggregate như một tập hợp trong bộ nhớ), chúng tôi có thể phát triển ứng dụng dựa trên cơ chế lưu trữ tạm trong bộ nhớ (in-memory persistence) nằm ẩn sau các interface của Repository, rồi sau đó mới cắm cơ chế lưu trữ thực tế vào sau khi đã có đủ thời gian cân nhắc kỹ lưỡng các lựa chọn.

Maria: Đỉnh thật đấy anh bạn.

Mitchell: Hoàn toàn chính xác.

Maria: Và rồi sao nữa?

Mitchell: Bùm một cái. Mọi thứ cất cánh và vận hành trơn tru. Chúng tôi đã bàn giao CollabOvation và ProjectOvation, mang về các quý kinh doanh liên tiếp đầy lợi nhuận.

Maria: Tiền vào như nước nhỉ!

> 💡 **Giải thích thêm:** Cụm từ gốc "Ka-ching" mô phỏng âm thanh mở ngăn kéo của chiếc máy tính tiền cơ học ngày xưa, là thành ngữ lóng trong tiếng Anh mang nghĩa tiền bạc thu về dồi dào, kiếm được lợi nhuận lớn.
> Nguồn tham khảo: [Merriam-Webster - Ka-ching definition](https://www.google.com/search?q=https://www.merriam-webster.com/dictionary/ka-ching)

Mitchell: Chuẩn không cần chỉnh. Sau đó, chúng tôi quyết định muốn hỗ trợ thêm các thiết bị di động bên cạnh các trình duyệt trên desktop vì thiết bị di động bùng nổ quá mạnh mẽ và lan tỏa tới mọi ngóc ngách. Với mục tiêu đó, chúng tôi sử dụng REST. Các thuê bao bắt đầu yêu cầu những tính năng như federated identity (định danh liên kết - cơ chế cho phép dùng chung tài khoản đăng nhập trên nhiều hệ thống độc lập) và bảo mật, cũng như các công cụ quản lý dự án và tài nguyên thời gian tinh vi hơn. Và rồi các nhà đầu tư mới lại muốn xem các báo cáo trên bảng điều khiển BI (Business Intelligence - Trí tuệ Doanh nghiệp) ưa thích của họ.

Maria: Tuyệt vời. Vậy là không chỉ có mỗi thiết bị di động bùng nổ. Hãy cho tôi biết cách các anh xử lý tất cả những đòi hỏi đó.

Mitchell: Nhóm phát triển đã quyết định rằng việc chuyển đổi sang Hexagonal Architecture (Kiến trúc Lục giác) là một lựa chọn hoàn toàn phù hợp để giải quyết tất cả các nhu cầu bổ sung này. Họ nhận thấy cách tiếp cận Ports and Adapters (Cổng và Bộ chuyển đổi - tên gọi khác của Hexagonal Architecture) mang lại khả năng thêm vào các loại client mới gần như tức thời theo nhu cầu. Điều tương tự cũng áp dụng cho các kiểu Cổng đầu ra (output Port), chẳng hạn như các cơ chế lưu trữ dữ liệu mới đầy sáng tạo như NoSQL, cùng các khả năng truyền thông điệp (messaging). Và tất cả những điều đó đều hướng thẳng tới điện toán đám mây (cloud).

Maria: Vậy là các anh hoàn toàn tự tin vào những thay đổi đó chứ?

Mitchell: Chắc chắn rồi.

Maria: Quá ấn tượng. Nếu không bị khuất phục trước tất cả những áp lực đó, điều đó chứng tỏ các anh đã đưa ra những lựa chọn xuất sắc, làm đòn bẩy giúp tiến xa hơn nữa.

Mitchell: Hoàn toàn chính xác. Vào thời điểm đó, chúng tôi bổ sung thêm hàng trăm khách hàng thuê bao mới mỗi tháng. Chúng tôi thực tế đã bổ sung thêm một dịch vụ để chuyển đổi dữ liệu hiện có từ các công cụ cộng tác doanh nghiệp cũ kỹ (legacy) lên đám mây của mình. Nhóm phát triển nhận định rằng định hướng SOA (Service-Oriented Architecture - Kiến trúc Hướng Dịch vụ) cho phép họ tổng hợp khối dữ liệu này một cách rất gọn gàng bằng Collection Aggregator của Mule. Nó có thể nằm ngay trên ranh giới dịch vụ trong khi bên trong vẫn sử dụng Hexagonal Architecture.

Maria: À, vậy là các anh không đưa SOA vào chỉ vì nghe nó có vẻ thời thượng. Các anh dùng nó khi nó thực sự có ý nghĩa. Quá chuẩn. Chúng ta hiếm khi thấy những quyết định sáng suốt như vậy trên diện rộng trong toàn ngành.

Mitchell: Vâng, thưa Maria, và đó thực sự là cách tiếp cận mà chúng tôi kiên trì theo đuổi xuyên suốt. Đó chính là kim chỉ nam dẫn lối thành công cho chúng tôi. Ví dụ, theo thời gian, chúng tôi bổ sung thêm TrackOvation — phần mềm theo dõi lỗi (defect tracking) của chúng tôi, được tích hợp chặt chẽ với ProjectOvation. Và khi các tính năng của ProjectOvation ngày càng nở rộ, giao diện người dùng trở nên ngày càng phức tạp. Bảng điều khiển (dashboard) của Product Owner hiển thị toàn bộ các sản phẩm Scrum và các lỗi trong hệ thống được cập nhật liên tục theo từng command (lệnh nghiệp vụ) của ứng dụng và event tương ứng. Vì các Product Owner ở các khách hàng thuê bao khác nhau có những góc nhìn ưu tiên khác nhau, điều đó khiến các dashboard càng trở nên phức tạp hơn nữa. Và lẽ dĩ nhiên, chúng tôi cũng phải hỗ trợ cả các thiết bị di động. Nhóm đã cân nhắc kỹ lưỡng giá trị của việc đưa vào mẫu kiến trúc CQRS.

Maria: CQRS (Command Query Responsibility Segregation - Phân tách Trách nhiệm Lệnh và Truy vấn)? Thôi nào Mitch, cái đó nghe đao to búa lớn quá. Đó có phải là một trong những canh bạc đầy bất định mà chúng ta không biết trước kết cục sẽ ra sao không? Liệu có phải là hành động tự đưa mình vào thế nguy hiểm không?

> 💡 **Giải thích thêm:** Cụm từ "walking off the plank" (bị bắt bước đi trên tấm ván bắc ra ngoài mạn tàu hải tặc để rơi xuống biển) là thành ngữ tiếng Anh mang nghĩa liều lĩnh tự đưa mình vào chỗ chết hoặc chấp nhận một rủi ro hủy diệt không lường trước được.
> Nguồn tham khảo: [Cambridge Dictionary - Walk the plank](https://www.google.com/search?q=https://dictionary.cambridge.org/dictionary/english/walk-the-plank)

Mitchell: Ồ, thực ra không đến mức như vậy. Một khi nhóm đã có lý do chính đáng để sử dụng CQRS nhằm giải tỏa sự xung đột ma sát giữa hai thế giới: thế giới ghi dữ liệu (command) và thế giới đọc dữ liệu (query), thì cứ thế toàn lực tiến lên phía trước và họ chưa từng phải hối tiếc nhìn lại.

Maria: Rất chuẩn xác. Đó có phải là khoảng thời gian mà các thuê bao bắt đầu đòi hỏi các tính năng yêu cầu xử lý phân tán (distributed processing) không anh?

Mitchell: Đúng vậy; nếu chúng tôi không làm đúng chỗ này thì chẳng mấy chốc sẽ chìm nghỉm trong sự phức tạp. Một số tính năng đòi hỏi phải chạy qua một chuỗi các tiến trình phân tán trước khi trả về kết quả cuối cùng. Nhóm ProjectOvation kiên quyết không bắt người dùng phải chờ đợi những tác vụ chạy lâu (long-running tasks) này và đối mặt với rủi ro bị timeout. Họ đã đưa vào một Kiến trúc Hướng Sự kiện (Event-Driven Architecture) toàn diện, ứng dụng mẫu kinh điển Pipes and Filters (Ống dẫn và Bộ lọc - mẫu kiến trúc xử lý dữ liệu tuần tự qua từng bộ lọc độc lập kết nối bằng ống dẫn) để quản lý luồng xử lý này.

Maria: Nhưng đó vẫn chưa phải là điểm dừng trên con đường đầy phức tạp của các anh, phải không? Đoạn đường đó gian nan đến mức nào?

Mitchell: Haha. Không, không đâu. Dường như chuyện đó chẳng bao giờ dừng lại. Tuy nhiên, khi cô sở hữu một đội ngũ kỹ sư thông minh, con đường đầy rẫy phức tạp bỗng nhẹ nhàng như một chuyến dạo chơi trong công viên. Trên thực tế, Kiến trúc Hướng Sự kiện đã đơn giản hóa rất nhiều khu vực trong bộ hệ thống đang ngày càng mở rộng.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000103_c017e61e56fdeca9a8720a002f6c0b97b680f64936e8c8a787c8436097d361f6.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000104_fba362b48617f9b573c1fbf4d9f2cdb576e035255a139d26df3d2dd13039f517.png)

Maria: Chuẩn quá rồi. Kể tiếp đi anh. Đó rõ ràng là một thời cơ tuyệt vời. Chúng ta đang tiến tới phần câu chuyện mà tôi yêu thích nhất rồi đây. Anh biết đấy . . . [mắt ánh lên vẻ lấp lánh của những con số $$$]

Mitchell: Kiến trúc của chúng tôi cho phép hệ thống mở rộng quy mô (scale) nhanh chóng và quản trị sự thay đổi xuất sắc đến mức RoaringCloud đã quyết định thâu tóm SaaSOvation với mức giá, ừm . . . tất cả những con số đó đều đã được công bố công khai trên hồ sơ tài chính rồi.

Maria: Tôi phải công nhận, và cực kỳ công khai là đằng khác. Với mức giá 50 đô la cho mỗi cổ phiếu phổ thông, đó là một hồ sơ công khai trị giá khoảng 3 tỷ đô la.

Mitchell: Trí nhớ về các con số tài chính của cô thật đáng nể! Và đó chính là động lực to lớn thúc đẩy chúng tôi phải làm cho phần tích hợp chuẩn chỉ tuyệt đối. Họ mang lại một lượng người dùng thuê bao khổng lồ mới, và lượng người dùng tăng vọt này thực tế đã bắt đầu gây áp lực nặng nề lên hạ tầng của ProjectOvation. Lúc này đã đến lúc phải phân tán và chạy song song hóa (parallelize) mô hình Pipes and Filters. Điều đó đòi hỏi phải đưa vào các tiến trình xử lý kéo dài (long-running processes), đôi khi còn được gọi là Saga.

Maria: Tuyệt quá. Anh có thể khẳng định dứt khoát rằng giai đoạn đó rất vui không?

Mitchell: Quả thực rất vui, nhưng trên hết là tính cấp bách bắt buộc phải làm.

Maria: Và dường như niềm vui đó chẳng bao giờ chấm dứt. Có lẽ một trong những chương bất ngờ nhất và thậm chí gây sốc nhất trong câu chuyện thành công dài kỳ của các anh đã diễn ra ngay sau đó.

Mitchell: Cô biết rõ quá rồi đấy. Giờ đây khi RoaringCloud đã nắm giữ vị thế độc quyền trên thị trường nhờ số lượng ứng dụng thuê bao khổng lồ cùng hàng triệu người dùng, chính phủ đã bắt đầu để mắt tới và tiến hành siết chặt kiểm soát ngành này. Một đạo luật mới đã được thông qua yêu cầu RoaringCloud phải truy vết mọi thay đổi diễn ra trong một dự án. Thực tế, cách tốt nhất để xử lý tình huống tuân thủ pháp lý này như một phần tự nhiên bên trong mô hình miền chính là áp dụng Event Sourcing (Lưu trữ Sự kiện - kỹ thuật lưu toàn bộ thay đổi trạng thái dưới dạng một chuỗi các sự kiện nối tiếp không thể chỉnh sửa).

Maria: Trời ạ, các anh chuẩn bị kỹ lưỡng thật. Thật là điên rồ. Ý tôi là, thực sự, thực sự điên rồ.

Mitchell: Đó thực sự là một cơn đau đầu dễ chịu, quả thật như vậy.

Maria: Điều khiến tôi vô cùng kinh ngạc là xuyên suốt ngần ấy năm, hạt nhân cốt lõi của các ứng dụng của các anh luôn dựa trên các mô hình phần mềm DDD. Ấy thế mà, rõ ràng DDD không hề cản trở các anh. Các anh dường như không phải trải qua bất kỳ sự chật vật nào vì nó.

Mitchell: Ngược lại hoàn toàn mới đúng. Chúng tôi tin tưởng vững chắc rằng chính nhờ việc lựa chọn DDD từ sớm, và dành thời gian thấu hiểu nó một cách thấu đáo, mà những tình huống kinh doanh cam go mà chúng tôi không thể né tránh — và cũng không hề muốn né tránh — đều đã được giải quyết một cách vô cùng êm đẹp.

Maria: Vâng, như tôi vẫn thường thích thốt lên: 'Ka-ching!' Một lần nữa cảm ơn anh, Mitchell. Chúng ta đã học được bài học về việc lựa chọn đúng kiến trúc có thể mang lại thành công vững bền ra sao, ngay tại chương trình 'Hiểu đúng về Phong cách Kiến trúc của bạn.'

Mitchell: Niềm vinh hạnh của tôi, Maria. Cảm ơn cô đã mời tôi tham gia.

Buổi trò chuyện đó có phần hơi dí dỏm khác thường, nhưng lại vô cùng hữu ích. Nó chứng minh rõ nét cách các ảnh hưởng kiến trúc được thảo luận trong các phần sau có thể được kết hợp hài hòa với DDD, và cách đưa từng yếu tố vào hệ thống đúng vào thời điểm chín muồi.

## Layers

Mẫu Layers Architecture [Buschmann et al.] được nhiều người coi là cội nguồn của mọi kiến trúc. Nó hỗ trợ các hệ thống đa tầng (N-tier) và do đó thường được sử dụng phổ biến trong các ứng dụng Web, doanh nghiệp và desktop. Ở đây, chúng ta tách biệt một cách chặt chẽ các mối bận tâm (concerns) khác nhau của ứng dụng hoặc hệ thống thành các tầng được định nghĩa rõ ràng.

> Hãy cô lập việc biểu đạt mô hình miền và logic nghiệp vụ, đồng thời loại bỏ bất kỳ sự phụ thuộc nào vào hạ tầng, giao diện người dùng, hoặc ngay cả logic ứng dụng không phải là logic nghiệp vụ. Hãy phân chia một chương trình phức tạp thành các tầng. Hãy phát triển một thiết kế bên trong mỗi tầng sao cho có tính gắn kết (cohesive) cao và chỉ phụ thuộc duy nhất vào các tầng bên dưới nó. [Evans, Ref, tr. 16]

Hình 4.1 thể hiện các tầng phổ biến trong một ứng dụng DDD sử dụng kiến trúc Layers truyền thống. Tại đây, Core Domain được cô lập cư trú tại một tầng

Hình 4.1 Kiến trúc Phân tầng (Layers Architecture) truyền thống trong đó áp dụng DDD

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000105_d4993e7f4c02f4dc75ba7e3319f12c93ae739649230c1ccb4ebf6983c9559df6.png)

119

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000106_6f24723144776bc4ee1888739d75631f851eddad8ed6b04c03f554e20bf06c36.png)

trong kiến trúc. Nằm phía trên nó là User Interface Layer và Application Layer. Nằm bên dưới nó là Infrastructure Layer.

Một nguyên tắc cốt yếu của kiến trúc này là mỗi tầng chỉ được phép liên kết (couple) với chính nó và các tầng bên dưới. Có những biến thể phân biệt trong phong cách này. Một Strict Layers Architecture (Kiến trúc Phân tầng Nghiêm ngặt) là kiến trúc chỉ cho phép liên kết trực tiếp tới tầng nằm ngay sát bên dưới nó. Ngược lại, một Relaxed Layers Architecture (Kiến trúc Phân tầng Nới lỏng) cho phép bất kỳ tầng cấp cao nào cũng có thể liên kết tới bất kỳ tầng nào nằm dưới nó. Vì cả User Interface và các Application Service thường xuyên cần sử dụng các thành phần hạ tầng, nên phần lớn, nếu không muốn nói là hầu hết, các hệ thống đều dựa trên nền tảng Relaxed Layers.

Các tầng thấp hơn trên thực tế có thể liên kết lỏng lẻo (loosely couple) với các tầng cao hơn, nhưng điều này chỉ diễn ra thông qua các cơ chế như Observer hoặc Mediator [Gamma et al.]; tuyệt đối không bao giờ có một tham chiếu trực tiếp từ tầng dưới lên tầng trên. Ví dụ, khi sử dụng Mediator, tầng cao hơn sẽ hiện thực hóa một interface được định nghĩa bởi tầng thấp hơn, sau đó truyền đối tượng hiện thực đó làm đối số xuống tầng thấp hơn. Tầng thấp hơn sẽ sử dụng đối tượng hiện thực đó mà hoàn toàn không cần biết nó cư trú ở vị trí nào về mặt kiến trúc.

User Interface chỉ được chứa duy nhất những đoạn mã giải quyết các mối bận tâm về góc nhìn hiển thị và yêu cầu của người dùng. Nó tuyệt đối không được chứa domain logic hay business logic (logic nghiệp vụ). Một số người có thể vội vã kết luận rằng vì giao diện người dùng yêu cầu validation (kiểm tra tính hợp lệ dữ liệu), nên nó ắt hẳn phải chứa business logic. Những kiểu validation xuất hiện ở User Interface không phải là những kiểu validation thuộc về (chỉ riêng) mô hình miền. Như đã được thảo luận trong Entities (Chương 5), chúng ta vẫn muốn giới hạn các phép xác thực thô (coarse-grained validations) mang tri thức nghiệp vụ sâu sắc chỉ nằm duy nhất trong mô hình miền.

Nếu các thành phần của User Interface có sử dụng các đối tượng từ mô hình miền, việc sử dụng này nhìn chung chỉ giới hạn ở việc hiển thị dữ liệu của đối tượng lên màn hình. Nếu áp dụng cách tiếp cận này, một Presentation Model (Chương 14) có thể được sử dụng để ngăn bản thân view (giao diện) biết về các đối tượng miền.

Vì người dùng có thể là con người hoặc các hệ thống khác, đôi khi tầng này sẽ cung cấp phương tiện để gọi từ xa các dịch vụ của một API dưới hình thức của một Open Host Service (Chương 13).

Các thành phần trong User Interface là các client trực tiếp của Application Layer. Các Application Service (Chương 14) cư trú trong Application Layer. Những dịch vụ này hoàn toàn khác biệt với Domain Service (Chương 7) và do đó hoàn toàn không chứa domain logic. Chúng có thể quản lý các transaction (giao dịch) lưu trữ và bảo mật. Chúng cũng có thể chịu trách nhiệm gửi các thông báo dựa trên Event tới các hệ thống khác và/hoặc soạn thảo các email để gửi tới người dùng. Các Application Service trong tầng này là những client trực tiếp của mô hình miền, mặc dù bản thân chúng không mang bất kỳ business logic nào. Chúng luôn giữ vai trò rất mỏng nhẹ, điều phối các thao tác được thực thi trên các đối tượng miền, chẳng hạn như Aggregate (Chương 10). Chúng là phương tiện chính yếu để diễn đạt các use cases hoặc user stories lên trên mô hình. Do đó, một chức năng phổ biến của một Application Service là nhận các tham số từ User Interface, sử dụng một Repository (Chương 12) để lấy về một thực thể Aggregate, và sau đó thực thi một thao tác command trên thực thể đó:

```java
@Transactional
public void commitBacklogItemToSprint(
        String aTenantId,
        String aBacklogItemId,
        String aSprintId) {
    TenantId tenantId = new TenantId(aTenantId);
    BacklogItem backlogItem = backlogItemRepository.backlogItemOfId(
            tenantId,
            new BacklogItemId(aBacklogItemId));
    Sprint sprint = sprintRepository.sprintOfId(
            tenantId,
            new SprintId(aSprintId));
    backlogItem.commitTo(sprint);
}

```

Nếu các Application Service của chúng ta trở nên phức tạp hơn nhiều so với ví dụ này, đó có thể là dấu hiệu cho thấy domain logic đang bị rò rỉ vào Application Service, và mô hình đang dần trở thành anemic (mô hình suy dinh dưỡng - Anemic Domain Model: mô hình chỉ chứa dữ liệu/getter/setter mà không có hành vi nghiệp vụ). Vì vậy, một best practice (thực tiễn tốt nhất) là luôn giữ cho các client của mô hình này thật mỏng. Khi cần tạo ra một Aggregate mới, Application Service sẽ sử dụng một Factory (Chương 11) hoặc hàm khởi tạo (constructor) của Aggregate để khởi tạo nó, rồi sử dụng Repository tương ứng để lưu trữ nó. Một Application Service cũng có thể sử dụng một Domain Service để hoàn thành một tác vụ đặc thù của miền được thiết kế dưới dạng một thao tác không trạng thái (stateless operation).

Khi mô hình miền được thiết kế để xuất bản các Domain Event (Chương 8), Application Layer có thể đăng ký các subscriber (bên đăng ký nhận tin) cho bất kỳ số lượng Event nào. Làm như vậy cho phép các Event được lưu trữ, chuyển tiếp và xử lý như một trong những nhiệm vụ của ứng dụng. Điều này giải phóng mô hình miền để nó chỉ cần nhận biết các mối bận tâm cốt lõi của chính mình, đồng thời giúp Domain Event Publisher (Chương 8) luôn mỏng nhẹ và hoàn toàn thoát khỏi sự phụ thuộc vào hạ tầng messaging.

Vì mô hình miền nắm giữ toàn bộ business logic đã được thảo luận rất chi tiết trong các chương khác, nội dung này sẽ không được nhắc lại ở đây. Dẫu vậy, vẫn có một số thách thức liên quan đến miền khi sử dụng kiến trúc Layers truyền thống. Việc sử dụng Layers có thể đòi hỏi Domain Layer phải sử dụng một số thành phần nhất định của Infrastructure. Tôi không hề nói rằng các đối tượng miền cốt lõi sẽ làm điều này, bởi chúng ta tuyệt đối phải tránh hoàn toàn điều đó. Tuy nhiên, việc tuân thủ nghiêm ngặt định nghĩa của Layers có thể đòi hỏi các implementation (phần triển khai cụ thể) của một số interface trong Domain Layer phải phụ thuộc vào các công nghệ do Infrastructure cung cấp.

Ví dụ, các interface Repository đòi hỏi các implementation phải sử dụng các thành phần, chẳng hạn như cơ chế lưu trữ dữ liệu, vốn được đặt tại Infrastructure. Điều gì sẽ xảy ra nếu chúng ta chỉ đơn thuần triển khai các interface Repository ngay trong Infrastructure? Vì Infrastructure Layer nằm bên dưới Domain Layer, các tham chiếu từ Infrastructure ngược lên Domain sẽ vi phạm các quy tắc của Layers Architecture. Dẫu vậy, việc tránh điều đó không có nghĩa là các đối tượng miền chính sẽ liên kết với Infrastructure. Để tránh điều đó, chúng ta có thể sử dụng các Module (Chương 9) triển khai để che giấu các lớp kỹ thuật:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000107_36916302071c845c2445380beb39142b050ad2dab5fe960590ab8fc6559cca59.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000108_432cd48632c23c9bc9f731097cf2df77d2e3f0eea9a666cfb82d143a2eb81b6a.png)

com.saasovation.agilepm.domain.model.product.impl

Như được chỉ ra trong Modules (Chương 9), MongoProductRepository có thể được đặt trong package đó. Tuy nhiên, đây không phải là cách duy nhất để giải quyết thách thức này. Chúng ta có thể quyết định triển khai các interface như vậy ngay trong Application Layer, điều này sẽ giữ vững các nguyên tắc của Layers. Hình 4.2 phác họa một góc nhìn về cách tiếp cận này. Nhưng làm như vậy có vẻ hơi gượng ép và khó chịu.

Có một phương pháp ưu việt hơn, như được thảo luận trong phần có tiêu đề 'Dependency Inversion Principle.'

Trong một Layers Architecture truyền thống, Infrastructure nằm ở đáy cùng. Những thứ như cơ chế lưu trữ dữ liệu và messaging cư trú tại đây. Các thông điệp có thể bao gồm những thông điệp được gửi bởi các hệ thống middleware nhắn tin doanh nghiệp hoặc các email (SMTP) hay tin nhắn văn bản (SMS) cơ bản hơn. Hãy nghĩ đến tất cả các thành phần kỹ thuật và framework cung cấp các dịch vụ cấp thấp cho ứng dụng. Những thứ đó thường được coi là một phần của Infrastructure. Các Layer cấp cao hơn liên kết tới các thành phần cấp thấp hơn để tái sử dụng các tiện ích kỹ thuật được cung cấp. Trong bối cảnh đó, một lần nữa chúng ta kiên quyết bác bỏ bất kỳ ý niệm nào về việc liên kết các đối tượng mô hình miền cốt lõi với Infrastructure.

Hình 4.2 Application Layer có thể chứa một số triển khai kỹ thuật của các interface được định nghĩa bởi Domain Layer.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000109_89f86183e2edbee8be75e17e114b84eb7976d16e384f7e627bf78e5c6b5ca772.png)

Các nhóm phát triển của SaaSOvation nhận thấy rằng việc đặt Infrastructure Layer ở dưới đáy cùng đã bộc lộ một số nhược điểm. Thứ nhất, nó khiến việc triển khai các khía cạnh kỹ thuật theo yêu cầu của Domain Layer trở nên khá đắng chát vì các nguyên tắc của Layers buộc phải bị vi phạm. Và trên thực tế, mã nguồn của họ rất khó kiểm thử. Làm thế nào họ có thể vượt qua bất lợi này?

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000110_8bca670e7b19e0afa80f53d7176eccb3d85719d39eeb63f4e671074e62a9cf03.png)

Liệu chúng ta có thể nhào nặn ra điều gì đó ngọt ngào hơn nếu chúng ta điều chỉnh lại thứ tự của các Tầng?

## Dependency Inversion Principle

Có một cách để cải tiến Layers Architecture truyền thống bằng cách điều chỉnh lại cách thức hoạt động của các dependency (sự phụ thuộc). Dependency Inversion Principle (DIP) được khởi xướng bởi Robert C. Martin và được mô tả chi tiết trong [Martin, DIP]. Định nghĩa chính thức phát biểu rằng:

> Các module cấp cao không nên phụ thuộc vào các module cấp thấp. Cả hai nên phụ thuộc vào abstractions (sự trừu tượng hóa/giao diện trừu tượng).
> Abstractions không nên phụ thuộc vào chi tiết. Chi tiết nên phụ thuộc vào abstractions.

Bản chất của định nghĩa này muốn truyền đạt rằng một thành phần cung cấp các dịch vụ cấp thấp (ở đây là Infrastructure) nên phụ thuộc vào các interface do các thành phần cấp cao định nghĩa (ở đây là User Interface, Application, và Domain). Mặc dù có nhiều cách để biểu đạt một kiến trúc sử dụng DIP, chúng ta có thể quy nạp nó về cấu trúc được hiển thị trong Hình 4.3.

## Does DIP Really Support All Those Layers?

Một số người sẽ kết luận rằng DIP thực chất chỉ có hai tầng: một tầng ở trên đỉnh và một tầng ở dưới đáy. Tầng ở trên đỉnh sẽ triển khai các interface trừu tượng được định nghĩa trong tầng ở đáy. Điều chỉnh Hình 4.3 cho khớp với nhận định này, Infrastructure Layer sẽ là tầng nằm trên đỉnh, còn User Interface Layer, Application Layer, và Domain Layer sẽ hợp thành tầng nằm dưới đáy. Bạn có thể thích hoặc không thích góc nhìn này về một kiến trúc DIP. Đừng lo lắng; Hexagonal [Cockburn] hay Kiến trúc Ports and Adapters chính là đích đến của toàn bộ quá trình tiến hóa này.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000111_ed814c4bf33e89aaafff6bb3bcb338610f70bec95942ced0a2f0d533571f5c17.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000112_8dd2e36f56da9f8afde774331e39836c674224a06ffd96e8ae6a345ce28c3a1e.png)

Hình 4.3 Các Tầng khả dĩ khi áp dụng Dependency Inversion Principle. Chúng ta chuyển Infrastructure Layer lên phía trên tất cả các tầng khác, cho phép nó triển khai các interface cho tất cả các Tầng bên dưới.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000113_bf0ddf7c657784885e307c03bb5d0ace4272d4937dadfd0fa55e4cfa7e7ead7a.png)

Từ kiến trúc trong Hình 4.3, chúng ta sẽ có một Repository được triển khai trong Infrastructure cho một interface được định nghĩa bên trong Domain:

```java
package com.saasovation.agilepm.infrastructure.persistence;

import com.saasovation.agilepm.domain.model.product.*;

public class HibernateBacklogItemRepository implements BacklogItemRepository {
    ...
    @Override
    @SuppressWarnings("unchecked")
    public Collection<BacklogItem> allBacklogItemsComittedTo(
            Tenant aTenant,
            SprintId aSprintId) {
        Query query = this.session().createQuery(
                "from -BacklogItem as _obj_ " +
                "where _obj_.tenant = ? and _obj_.sprintId = ?");
        query.setParameter(0, aTenant);
        query.setParameter(1, aSprintId);
        return (Collection<BacklogItem>) query.list();
    }
    ...
}

```
